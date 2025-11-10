# 🚀 Wolf Market Analyzer - Render.com Deployment

## Render.com Käyttöönotto-opas

Tämä opas auttaa sinua julkaisemaan Wolf Market Analyzer -sovelluksen Render.com-palveluun.

---

## 📋 Esivalmistelut

### 1. Tarvittavat Tilit ja Avaimet

Tarvitset seuraavat:

- ✅ **Render.com tili** (ilmainen: https://render.com)
- ✅ **GitHub-tili** (jos et ole vielä pushannut koodia)
- ✅ **Binance API avaimet** (valinnainen, mutta suositeltu livetoimintoon)
- ✅ **Anthropic Claude API avain** (AI-analyysejä varten)

### 2. GitHub Repository

Varmista että koodisi on GitHubissa:

```bash
# Jos et ole vielä pushannut:
git add .
git commit -m "Prepare for Render deployment"
git push -u origin claude/finnish-app-development-011CUznvzaNBspwCfjRCQeSR
```

---

## 🎯 Nopea Käyttöönotto (Blueprint Method)

### Vaihtoehto A: Automaattinen käyttöönotto render.yaml:lla

1. **Kirjaudu Render.com**
   - Mene osoitteeseen: https://render.com
   - Kirjaudu sisään GitHub-tilillä

2. **Luo uusi Blueprint**
   - Klikkaa "New" → "Blueprint"
   - Valitse tämä repository
   - Render havaitsee automaattisesti `render.yaml`-tiedoston

3. **Lisää Environment Variables**

   Render kysyy seuraavia:

   ```
   BINANCE_API_KEY=oTuVzgZOlMJBnf9BUi7Cf4fPH5ueUei9SjTjWMgUCAg9tWm7fVC3qJNZC3C6V4Ib
   BINANCE_API_SECRET=UdhLIIhTz1tIB2qAZoMj172oZEfODLZjTVWHZ0kmjAhGheWB094MMRPMk0QD2O1J
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

   Muut muuttujat on jo määritelty `render.yaml`:ssa.

4. **Käynnistä Deploy**
   - Klikkaa "Apply"
   - Render alkaa buildaamaan sovellusta
   - Prosessi kestää 3-5 minuuttia

5. **Valmis!** 🎉
   - Saat URL-osoitteen muodossa: `https://wolf-market-analyzer.onrender.com`

---

## 🔧 Vaihtoehto B: Manuaalinen käyttöönotto

Jos haluat tehdä käsin ilman render.yaml:

### 1. Luo Web Service

1. Mene Render Dashboard → "New" → "Web Service"
2. Valitse GitHub repository
3. Anna nimi: `wolf-market-analyzer`

### 2. Määritä Build & Start

- **Environment**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**:
  ```bash
  python web_dashboard.py --host 0.0.0.0 --port $PORT
  ```

### 3. Aseta Environment Variables

Mene "Environment" -välilehdelle ja lisää:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `BINANCE_API_KEY` | `oTuVzgZOlMJBnf9BUi7Cf4fPH5ueUei9SjTjWMgUCAg9tWm7fVC3qJNZC3C6V4Ib` |
| `BINANCE_API_SECRET` | `UdhLIIhTz1tIB2qAZoMj172oZEfODLZjTVWHZ0kmjAhGheWB094MMRPMk0QD2O1J` |
| `ANTHROPIC_API_KEY` | `your_key_here` |
| `WATCHLIST` | `BTC/USDT,ETH/USDT,SOL/USDT,AVAX/USDT,ARB/USDT` |
| `ACCOUNT_SIZE` | `10000` |
| `RISK_PER_TRADE_PERCENT` | `1.0` |
| `MAX_OPEN_POSITIONS` | `3` |
| `MIN_RISK_REWARD` | `2.0` |
| `MIN_PATTERN_CONFIDENCE` | `0.65` |
| `DEFAULT_TIMEFRAME` | `4h` |

### 4. Valitse Plan

- **Free Plan**: Riittää testaukseen
  - 512 MB RAM
  - Nukkuu 15 min inaktiivisuuden jälkeen
  - 750 tuntia kuukaudessa ilmaiseksi

- **Starter Plan ($7/kk)**: Tuotantokäyttöön
  - Ei nuku
  - Enemmän resursseja

### 5. Deploy

- Klikkaa "Create Web Service"
- Build alkaa automaattisesti

---

## ✅ Varmista että toimii

### 1. Tarkista Logs

Deployment jälkeen, mene "Logs" -välilehdelle. Pitäisi näkyä:

```
🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺
   WOLF MARKET ANALYZER - WEB DASHBOARD
🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺🐺

Configuration:
  Watchlist: BTC/USDT, ETH/USDT, SOL/USDT, AVAX/USDT, ARB/USDT
  Account Size: $10,000.00
  Risk per Trade: 1.0%

 * Running on all addresses (0.0.0.0)
 * Running on http://0.0.0.0:10000
```

### 2. Testaa sovellusta

Avaa Renderin antama URL (esim. `https://wolf-market-analyzer.onrender.com`)

Pitäisi näkyä:
- ✅ Dashboard etusivu
- ✅ Watchlist hintatiedoilla
- ✅ System Status: Online
- ✅ Kaikki linkit toimivat

### 3. Testaa API Endpoints

```bash
# Status endpoint
curl https://your-app.onrender.com/api/status

# Watchlist endpoint
curl https://your-app.onrender.com/api/watchlist

# Analyze endpoint (korvaa BTC/USDT haluamallasi)
curl https://your-app.onrender.com/api/analyze/BTC/USDT
```

---

## 🔄 Automaattiset Päivitykset

Render päivittää sovelluksen automaattisesti kun pushaat GitHubiin:

```bash
# Tee muutoksia koodiin
git add .
git commit -m "Update feature X"
git push

# Render havaitsee automaattisesti ja deployaa uuden version
```

---

## ⚠️ Huomioitavaa

### Free Plan Rajoitukset

1. **Nukkuminen**: Sovellus nukkuu 15 min inaktiivisuuden jälkeen
   - Ensimmäinen lataus sen jälkeen kestää 30-60 sekuntia
   - Ratkaisu: Käytä UptimeRobot tai vastaavaa ping-palvelua

2. **750h/kk rajoitus**: Riittää useimmille käyttötapauksille
   - Jos tarvitset 24/7 käytettävyyttä, päivitä Starter-planiin

3. **RAM-rajoitus**: 512 MB
   - Wolf Market Analyzer toimii hyvin tällä
   - Jos lisäät paljon ominaisuuksia, voi tarvita enemmän

### Tietoturva

**TÄRKEÄÄ**: Älä koskaan commitoi API-avaimia Gitiin!

Avamet tulee aina asettaa Render Environment Variables -osiossa, ei `.env`-tiedostoon repositoryssä.

Jos vahingossa commitoit avaimet:
1. Vaihda avamet välittömästi Binancessa/Anthropicissa
2. Poista vanhat commitit historiasta (`git filter-branch` tai BFG Repo-Cleaner)

### Binance API Oikeudet

Tuotantokäytössä suosittelen:
- ✅ Vain **READ** oikeudet (ei trading-oikeuksia)
- ✅ IP-rajoitus (lisää Renderin IP)
- ❌ Ei withdrawal-oikeuksia

---

## 📊 Monitorointi

### Render Dashboard

Seuraa:
- **Metrics**: CPU, RAM, response times
- **Logs**: Virheet ja varoitukset
- **Events**: Deploy-historia

### Ulkoiset palvelut (valinnainen)

- **UptimeRobot**: Ping sovellusta 5min välein estääksesi nukkumisen
- **Sentry**: Virheenseuranta
- **Google Analytics**: Käyttäjäanalytiikka

---

## 🐛 Troubleshooting

### Build Failed

**Virhe**: `ERROR: Could not find a version...`

**Ratkaisu**: Tarkista että `requirements.txt` on oikein. Käytä:
```bash
pip freeze > requirements.txt
```

### Application Error (503)

**Virhe**: Sovellus ei käynnisty

**Ratkaisu**:
1. Tarkista Logs
2. Varmista että `PORT` environment variable on käytössä
3. Tarkista että start command on oikein

### Binance API Not Working

**Virhe**: `Connection refused` tai `API key invalid`

**Ratkaisu**:
1. Tarkista että Environment Variables on asetettu oikein
2. Varmista että API key on valid
3. Tarkista Binance IP restrictions
4. Demo-mode toimii ilman API-avaimia

---

## 💡 Optimointitips

### 1. Lisää Health Check Endpoint

Render voi pingata health check endpointia:

```python
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200
```

Aseta Render Dashboardissa: Settings → Health Check Path = `/health`

### 2. Käytä Gunicorn (Tuotantoon)

Lisää `requirements.txt`:
```
gunicorn==21.2.0
```

Muuta start command:
```bash
gunicorn -w 4 -b 0.0.0.0:$PORT src.web.app:app
```

### 3. Enable Caching

Lisää Redis Render.com:sta cachen parantamiseksi (maksullinen feature).

---

## 📚 Lisäresurssit

- [Render.com Documentation](https://render.com/docs)
- [Flask Production Best Practices](https://flask.palletsprojects.com/en/3.0.x/deploying/)
- [CCXT Documentation](https://docs.ccxt.com/)

---

## 🎉 Valmista!

Sovelluksesi on nyt käynnissä Render.com:ssa ja saatavilla koko maailmalle!

**Seuraavat askeleet:**
1. ✅ Testaa kaikki ominaisuudet
2. ✅ Aseta UptimeRobot estämään nukkuminen (free plan)
3. ✅ Jaa URL kavereillesi
4. ✅ Seuraa markkinoita ja tee parempia tradeja! 🐺📈

---

**Trade like a wolf, not a sheep!** 🐺
