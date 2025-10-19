# 🚀 Quick Start Guide

## GitHub → Replit in 5 minuten

### Stap 1: Maak GitHub Repository (2 min)

```bash
# Lokaal
mkdir makelaar-contract-generator
cd makelaar-contract-generator
git init

# Kopieer alle bestanden van de artifacts
# Zie hieronder voor volledige file lijst

git add .
git commit -m "Initial commit"

# Maak repository op GitHub
# Dan:
git remote add origin https://github.com/YOUR-USERNAME/makelaar-contract-generator.git
git branch -M main
git push -u origin main
```

### Stap 2: Import in Replit (1 min)

1. Ga naar [replit.com](https://replit.com)
2. Klik **"+ Create Repl"**
3. Kies **"Import from GitHub"**
4. Plak: `https://github.com/YOUR-USERNAME/makelaar-contract-generator`
5. Klik **"Import from GitHub"**

### Stap 3: Upload Template (1 min)

1. In Replit, open **Files** sidebar
2. Navigeer naar `backend/templates/`
3. Klik **"Upload file"**
4. Upload je `Template document.docx`
5. Hernoem naar exact: `template.docx`

### Stap 4: Run! (30 sec)

1. Klik de grote groene **"Run"** knop
2. Wacht op package installatie (~1-2 min eerste keer)
3. Open de gegenereerde URL
4. Klik **"Maak Demo Contract"** om te testen

### Stap 5: Test (30 sec)

✅ Je zou nu moeten zien:
- Groene "Online" status badge
- Demo contract in de lijst
- API tester werkt

## 📁 Complete File Lijst

Je hebt deze bestanden nodig in je GitHub repo:

### Root Files
```
makelaar-contract-generator/
├── main.py                       ← Artifact "File 1"
├── requirements.txt              ← Zie hieronder
├── .replit                       ← Zie hieronder
├── .gitignore                    ← Artifact "File 5"
├── .env.example                  ← Artifact "File 6"
├── README.md                     ← Artifact "File 7"
├── QUICK_START.md               ← Dit bestand
└── LICENSE                       ← MIT license tekst
```

### Backend Files
```
backend/
├── __init__.py                   ← Artifact "File 2"
├── api.py                        ← Eerder artifact (updated versie)
├── document_processor.py         ← Eerder artifact
├── word_generator.py             ← Eerder artifact
├── database.py                   ← Artifact "File 3"
├── uploads/.gitkeep
├── generated_contracts/.gitkeep
└── templates/
    └── README.md                 ← Artifact "File 8"
```

### Frontend Files
```
frontend/
└── index.html                    ← Artifact "File 4"
```

### Docs (optioneel)
```
docs/
├── API.md                        ← Zie hieronder
├── SETUP.md                      ← Zie hieronder
└── DEPLOYMENT.md                 ← Zie hieronder
```

## 📝 requirements.txt

```txt
# Web Framework
flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0

# Document Processing
python-docx==1.1.0
docxtpl==0.16.7
Pillow==10.1.0

# PDF Processing
PyPDF2==3.0.1

# Utilities
werkzeug==3.0.1
python-dotenv==1.0.0

# Voor later (te zwaar voor Replit free tier):
# easyocr==1.7.0
# opencv-python-headless==4.8.1.78
```

## 📝 .replit

```toml
run = "python main.py"
entrypoint = "main.py"
modules = ["python-3.11"]

hidden = [".pythonlibs", ".config", "__pycache__"]

[nix]
channel = "stable-23_11"

[deployment]
run = ["sh", "-c", "python main.py"]
deploymentTarget = "cloudrun"

[env]
FLASK_ENV = "production"
PYTHONUNBUFFERED = "1"

[[ports]]
localPort = 5000
externalPort = 80

[languages.python3]
pattern = "**/*.py"

[languages.python3.languageServer]
start = "pylsp"
```

## 🎯 Checklist

Voordat je pushed naar GitHub:

- [ ] Alle bestanden aangemaakt
- [ ] `.gitignore` correct ingesteld
- [ ] `requirements.txt` compleet
- [ ] `.replit` configuratie klopt
- [ ] `backend/templates/README.md` aanwezig
- [ ] `.gitkeep` files in lege folders
- [ ] Template NIET in git (te groot)
- [ ] `.env` NIET in git (secret keys)

## ⚡ Snelle Commands

```bash
# Maak alle folders
mkdir -p backend/uploads backend/generated_contracts backend/templates frontend docs

# Maak .gitkeep files
touch backend/uploads/.gitkeep
touch backend/generated_contracts/.gitkeep

# Maak __init__.py
touch backend/__init__.py

# Test lokaal (optioneel)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
# Open http://localhost:5000
```

## 🆘 Troubleshooting

### "Module not found"
```bash
# In Replit Shell:
pip install -r requirements.txt
```

### "Template not found"
- Check naam: exact `template.docx` (lowercase)
- Check locatie: `backend/templates/template.docx`
- Refresh Replit file tree

### "Port already in use"
- Stop de Repl
- Klik "Kill" in Shell
- Run opnieuw

### "Out of memory"
- Replit free tier heeft beperkte resources
- Gebruik mock OCR mode (standaard)
- Upgrade naar Hacker plan ($7/maand) indien nodig

## ✅ Success!

Als alles werkt zie je:

```
═══════════════════════════════════════════════════════════════════
🏠 MAKELAAR CONTRACT GENERATOR
═══════════════════════════════════════════════════════════════════
🌐 Server: http://0.0.0.0:5000
📊 Status: http://0.0.0.0:5000/api/status
🧪 Demo: POST http://0.0.0.0:5000/api/demo/populate
🔧 Environment: Replit
═══════════════════════════════════════════════════════════════════
```

En in je browser:
- ✅ Groene status badge
- ✅ "Maak Demo" knop werkt
- ✅ API tester toont JSON

## 🎉 Volgende Stappen

1. Test de demo contract feature
2. Upload een echt document
3. Pas het Word template aan
4. Configureer email notificaties (optioneel)
5. Deploy naar productie (zie DEPLOYMENT.md)

## 📞 Hulp Nodig?

- 📖 Lees de volledige docs in `/docs`
- 💬 Open een [GitHub Issue](https://github.com/YOUR-USERNAME/makelaar-contract-generator/issues)
- 📧 Email: support@example.com

**Happy coding! 🚀**
