# Frame Pack Access Guide

## 🚀 Frame Pack is Running!

The server is successfully running on port 7860. Here are the ways to access it:

### Access URLs (try in order):

1. **Standard localhost**: http://localhost:7860
2. **WSL IP address**: http://172.25.244.103:7860
3. **Alternative**: http://127.0.0.1:7860

### If Still Can't Connect:

#### 1. Windows Firewall
- Windows Defender might be blocking the connection
- Try temporarily disabling Windows Firewall for private networks

#### 2. WSL2 Port Forwarding
Run this in Windows PowerShell (as Administrator):
```powershell
netsh interface portproxy add v4tov4 listenport=7860 listenaddress=0.0.0.0 connectport=7860 connectaddress=172.25.244.103
```

#### 3. Alternative: Use Port Forwarding
In a new WSL terminal:
```bash
ssh -L 7860:localhost:7860 localhost
```

### Verify Server is Running:
```bash
# Check process
ps aux | grep demo_gradio

# Check port
ss -tuln | grep 7860

# Test with curl
curl http://localhost:7860
```

### Server Status:
- ✅ Process running (PID: 319763)
- ✅ Port 7860 open and listening
- ✅ Server responding to requests
- ✅ 6.93GB VRAM available

The Frame Pack GUI should show:
- Image upload area on the left
- Video generation progress on the right
- Prompt input field
- Generate button

Once you can access it, you can start generating videos!