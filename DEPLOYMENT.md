# DessertAble - Deployment Guide

This guide covers multiple hosting options for deploying your DessertAble application to production.

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- ✅ Google Places API key
- ✅ Production-ready SECRET_KEY (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- ✅ All environment variables ready
- ✅ Your code pushed to a Git repository (GitHub recommended)

---

## 🌟 Recommended Option: Render (Easiest)

**Best for:** Beginners, quick deployment, free tier available

### Why Render?
- ✅ Free tier with 750 hours/month
- ✅ Automatic deploys from GitHub
- ✅ Built-in HTTPS
- ✅ Easy environment variable management
- ✅ Persistent disk storage for SQLite

### Deployment Steps:

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `DessertAble` repository

3. **Configure Service**
   ```
   Name: dessertable
   Region: Choose closest to you
   Branch: main
   Root Directory: (leave blank)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn run:app
   ```

4. **Set Environment Variables**
   - Click "Environment" tab
   - Add these variables:
     ```
     FLASK_ENV=production
     GOOGLE_PLACES_API_KEY=your_actual_api_key_here
     SECRET_KEY=your_generated_secret_key_here
     ```

5. **Add Persistent Disk (for SQLite)**
   - Click "Disks" → "Add Disk"
   - Name: `dessertable-data`
   - Mount Path: `/opt/render/project/src/data`
   - Size: 1 GB (free tier)

6. **Deploy**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment
   - Your app will be live at `https://dessertable-xxxx.onrender.com`

**Cost:** FREE (with 750 hours/month on free tier)

---

## 🚀 Alternative: Railway (Very Easy)

**Best for:** Quick deployment, modern interface

### Steps:

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Deploy from GitHub**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `DessertAble` repository
   - Railway auto-detects Python and Flask

3. **Add Environment Variables**
   - Go to "Variables" tab
   - Add:
     ```
     FLASK_ENV=production
     GOOGLE_PLACES_API_KEY=your_api_key
     SECRET_KEY=your_secret_key
     PORT=5000
     ```

4. **Add Volume (for SQLite persistence)**
   - Click "Settings" → "Volumes"
   - Mount path: `/app/data`
   - Size: 1 GB

5. **Generate Domain**
   - Go to "Settings" → "Networking"
   - Click "Generate Domain"
   - Your app will be at `https://dessertable-production.up.railway.app`

**Cost:** FREE ($5 credit/month on free tier, enough for small apps)

---

## ☁️ AWS Option 1: Elastic Beanstalk (Recommended AWS)

**Best for:** AWS ecosystem, scalability, automatic management

### Steps:

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize Elastic Beanstalk**
   ```bash
   cd /path/to/DessertAble
   eb init
   ```
   - Choose your region
   - Create new application: `dessertable`
   - Platform: Python 3.11
   - Do NOT set up CodeCommit
   - Do NOT set up SSH

3. **Create `.ebextensions/python.config`** (already provided in this repo)

4. **Create Environment**
   ```bash
   eb create dessertable-env
   ```

5. **Set Environment Variables**
   ```bash
   eb setenv FLASK_ENV=production \
            GOOGLE_PLACES_API_KEY=your_api_key \
            SECRET_KEY=your_secret_key
   ```

6. **Deploy**
   ```bash
   eb deploy
   ```

7. **Open App**
   ```bash
   eb open
   ```

**Important for SQLite on EB:**
- SQLite data is NOT persistent by default on EB
- For production, consider upgrading to RDS (PostgreSQL/MySQL)
- Or use EFS (Elastic File System) for persistent storage

**Cost:** ~$10-30/month (no free tier for EB environments)

---

## ☁️ AWS Option 2: Lightsail (Simpler AWS)

**Best for:** Simple AWS deployment, predictable pricing

### Steps:

1. **Create Lightsail Instance**
   - Go to AWS Lightsail console
   - Click "Create instance"
   - Platform: Linux/Unix
   - Blueprint: OS Only → Ubuntu 22.04
   - Plan: $3.50/month (512 MB RAM)

2. **Connect via SSH**
   - Click instance → "Connect using SSH"

3. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv git nginx
   ```

4. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/DessertAble.git
   cd DessertAble
   ```

5. **Setup Application**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Create .env File**
   ```bash
   nano .env
   ```
   Add:
   ```
   FLASK_ENV=production
   GOOGLE_PLACES_API_KEY=your_api_key
   SECRET_KEY=your_secret_key
   ```

7. **Setup Gunicorn Service**
   ```bash
   sudo nano /etc/systemd/system/dessertable.service
   ```

   Add:
   ```ini
   [Unit]
   Description=DessertAble Flask App
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/DessertAble
   Environment="PATH=/home/ubuntu/DessertAble/venv/bin"
   ExecStart=/home/ubuntu/DessertAble/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 run:app

   [Install]
   WantedBy=multi-user.target
   ```

8. **Setup Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/dessertable
   ```

   Add:
   ```nginx
   server {
       listen 80;
       server_name your_lightsail_ip;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /static {
           alias /home/ubuntu/DessertAble/app/static;
       }
   }
   ```

9. **Enable and Start Services**
   ```bash
   sudo ln -s /etc/nginx/sites-available/dessertable /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   sudo systemctl start dessertable
   sudo systemctl enable dessertable
   ```

10. **Configure Firewall**
    - In Lightsail console, go to "Networking" tab
    - Add rule: HTTP (port 80)

**Cost:** $3.50-10/month

---

## 🌊 Alternative: Fly.io

**Best for:** Global deployment, Docker-based

### Steps:

1. **Install Fly CLI**
   ```bash
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Launch App** (from your project directory)
   ```bash
   fly launch
   ```
   - Name: dessertable
   - Region: Choose closest
   - Don't deploy yet: No
   - Would you like to setup a database: No

4. **Set Environment Variables**
   ```bash
   fly secrets set FLASK_ENV=production \
                    GOOGLE_PLACES_API_KEY=your_api_key \
                    SECRET_KEY=your_secret_key
   ```

5. **Create Volume (for SQLite)**
   ```bash
   fly volumes create dessertable_data --size 1
   ```

6. **Update fly.toml**
   Add under `[mounts]`:
   ```toml
   [mounts]
     source = "dessertable_data"
     destination = "/app/data"
   ```

7. **Deploy**
   ```bash
   fly deploy
   ```

**Cost:** FREE (with generous free tier)

---

## 🐍 PythonAnywhere (Python-Specific)

**Best for:** Python developers, very simple setup

### Steps:

1. **Create Account**
   - Go to https://www.pythonanywhere.com
   - Create free account

2. **Upload Code**
   - Go to "Files" tab
   - Upload your repository or clone from GitHub

3. **Create Virtual Environment**
   ```bash
   mkvirtualenv dessertable --python=python3.11
   cd DessertAble
   pip install -r requirements.txt
   ```

4. **Configure Web App**
   - Go to "Web" tab
   - Add new web app
   - Framework: Flask
   - Python version: 3.11
   - Path to Flask app: `/home/yourusername/DessertAble/run.py`

5. **Set Environment Variables**
   - In Web tab, scroll to "Environment variables"
   - Add your variables

6. **Configure WSGI**
   - Edit the WSGI file
   - Point it to your app

7. **Reload Web App**

**Cost:** FREE (with limitations) or $5/month

---

## 🔧 Production Considerations

### Database
**SQLite Limitations:**
- Not ideal for high-concurrency
- File-based storage can be lost on some platforms
- No built-in replication

**Recommended for Production:**
- **PostgreSQL** (most platforms offer managed PostgreSQL)
- Update `requirements.txt`: add `psycopg2-binary`
- Update connection string in config

### Environment Variables
Always set in production:
```bash
FLASK_ENV=production
GOOGLE_PLACES_API_KEY=your_production_key
SECRET_KEY=your_32_byte_random_key
DATABASE_URL=postgresql://... (if using PostgreSQL)
```

### Security
- ✅ Use HTTPS (most platforms provide this automatically)
- ✅ Set strong SECRET_KEY
- ✅ Restrict API key (HTTP referrers in Google Cloud Console)
- ✅ Set `DEBUG=False` in production

### Performance
- Use gunicorn with multiple workers: `gunicorn --workers 4 run:app`
- Enable caching (Redis recommended for production)
- Consider CDN for static files

---

## 📊 Cost Comparison

| Platform | Free Tier | Paid Tier | Best For |
|----------|-----------|-----------|----------|
| **Render** | ✅ 750hrs/mo | $7/month | Easiest deployment |
| **Railway** | ✅ $5 credit/mo | $5-20/month | Modern interface |
| **Fly.io** | ✅ Generous | $5-15/month | Global deployment |
| **PythonAnywhere** | ✅ Limited | $5/month | Python beginners |
| **AWS Lightsail** | ❌ | $3.50-10/month | Simple AWS |
| **AWS EB** | ❌ | $10-30/month | AWS ecosystem |

---

## 🎯 Recommendation

**For Beginners:** Start with **Render** or **Railway**
- Easiest setup
- Free tier to test
- Automatic HTTPS
- GitHub integration

**For AWS Users:** Use **Lightsail** first, then **Elastic Beanstalk** when you need to scale

**For Global Reach:** Use **Fly.io** (apps deployed to multiple regions)

---

## 🆘 Troubleshooting

### App won't start
- Check logs: `render logs` or platform equivalent
- Verify all environment variables are set
- Ensure gunicorn is in requirements.txt

### Database errors
- Make sure disk/volume is mounted correctly
- Check file permissions
- Consider upgrading to PostgreSQL for production

### API errors
- Verify Google API key is set correctly
- Check API key restrictions in Google Cloud Console
- Ensure billing is enabled in Google Cloud

---

## 📚 Additional Resources

- [Flask Deployment Documentation](https://flask.palletsprojects.com/en/latest/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Render Python Guide](https://render.com/docs/deploy-flask)
- [AWS Elastic Beanstalk Python](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html)

---

**Need help?** Open an issue on GitHub or check the troubleshooting section above.
