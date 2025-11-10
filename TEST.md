# 🧪 Testausohje - Wolf Market Analyzer

## Nopea Testaus (EI vaadi API-avaimia)

### 1. Demo-moodi (suositeltu aloittelijoille)
```bash
cd /home/user/Trading-App
source venv/bin/activate
python demo.py
```

**Mitä tämä tekee:**
- ✅ Generoi realistista testidataa
- ✅ Tunnistaa FOOS4-kuvioita
- ✅ Laskee tekniset indikaattorit (RSI, MACD, trendit)
- ✅ Skannaa watchlistin
- ✅ Näyttää AI-analyysi esimerkin
- ⏱️ Kestää: ~10 sekuntia

**Tulos:**
```
🐺 WOLF MARKET ANALYZER - DEMO MODE

✓ Pattern Recognition: 2 setups found
✓ Technical Indicators: RSI, MACD, Trend
✓ Watchlist Scan: 4 symbols analyzed
✓ All core features working
```

---

## Oikealla Datalla (vaatii Binance API)

### 2. Konfiguraation tarkistus
```bash
python main.py --config
```

**Näyttää:**
- ✓/✗ Binance API yhteys
- ✓/✗ Claude AI yhteys
- Watchlist-asetukset
- Riskinhallinta-parametrit

### 3. Bitcoin-analyysi
```bash
python main.py --analyze BTC/USDT
```

**Mitä tämä tekee:**
- Hakee oikeaa BTC-dataa Binancesta
- Tunnistaa kuviot (triangles, breaks)
- Laskee entry/stop/target-tasot
- Generoi kaavion (tallentuu charts/-kansioon)
- AI-analyysi (jos Claude API konfiguroitu)

### 4. Päivittäinen briefing
```bash
python main.py --brief
```

**Näyttää:**
- Watchlist-yhteenveto
- Aktiiviset setupit
- Markkinatilanne
- AI-suositukset

### 5. Koko watchlistin skannaus
```bash
python main.py --scan
```

**Skannaa kaikki:**
- BTC/USDT
- ETH/USDT
- SOL/USDT
- AVAX/USDT
- ARB/USDT

**Näyttää:**
- Top 5 setuppia confidence-järjestyksessä
- Entry/Stop/Target jokaiselle
- Risk:Reward-suhde

---

## API-Avainten Lisääminen

### Binance API (markkinadata)

1. **Mene:** https://www.binance.com/en/my/settings/api-management
2. **Luo API Key:**
   - Nimi: "Wolf Analyzer"
   - Oikeudet: ✓ Enable Reading (EI trading!)
   - IP Whitelist: Lisää IP-osoitteesi
3. **Kopioi:**
   - API Key
   - Secret Key
4. **Lisää .env-tiedostoon:**
   ```bash
   nano .env
   ```
   Päivitä:
   ```
   BINANCE_API_KEY=your_key_here
   BINANCE_API_SECRET=your_secret_here
   ```

### Anthropic Claude API (AI-analyysi)

1. **Mene:** https://console.anthropic.com
2. **Luo API Key**
3. **Lisää .env-tiedostoon:**
   ```
   ANTHROPIC_API_KEY=sk-ant-...your_key
   ```

### Testaa yhteys
```bash
python main.py --config
```

Pitäisi näyttää:
```
Binance API: ✓ Connected
Claude AI: ✓ Connected
```

---

## Yleisimmät ongelmat

### "Failed to connect to Binance"

**Syy:** API-avaimet puuttuu tai rajoitetut

**Ratkaisu:**
1. Tarkista .env-tiedoston avaimet
2. Tarkista Binance IP whitelist
3. Kokeile ilman avaimia (public data):
   ```bash
   # .env tiedostossa:
   BINANCE_API_KEY=
   BINANCE_API_SECRET=
   ```

### "No patterns detected"

**Syy:** Markkinat eivät ole juuri nyt sopivissa kuvioissa

**Ratkaisu:**
- Normaalia! Ei aina ole setuppia
- Kokeile eri timeframea: `--timeframe 1d`
- Kokeile toista symbolia
- Käytä demo.py:tä nähdäksesi miten toimii

### "AI analysis unavailable"

**Syy:** Claude API key puuttuu

**Ratkaisu:**
1. Hanki key: https://console.anthropic.com
2. Lisää .env:iin
3. Testaa: `python main.py --config`

### "Module not found"

**Syy:** Virtual environment ei ole aktiivinen

**Ratkaisu:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## Päivittäinen Käyttö (10 min)

### Aamu (7:00)
```bash
python main.py --brief
```
Lue briefing kahvilla ☕

### Päivän aikana (kun aikaa)
```bash
python main.py --scan
```
Tarkista uudet setupit 🔍

### Kun haluat analysoida
```bash
python main.py --analyze BTC/USDT
```
Syväanalyysi ennen kauppaa 📊

### Ilta (kauppojen jälkeen)
```bash
# Phase 2:ssa tulossa:
python main.py --journal
```
Kirjaa kaupat ja saa AI-coachingia 🎓

---

## Testaa Kaikki Ominaisuudet

### ✅ Checklist

```bash
# 1. Demo (ei vaadi API:ta)
python demo.py

# 2. Konfiguraatio
python main.py --config

# 3. Yksittäinen analyysi
python main.py --analyze BTC/USDT --no-chart

# 4. Watchlist scan
python main.py --scan

# 5. Daily brief
python main.py --brief

# 6. Kaavion generointi
python main.py --analyze ETH/USDT

# 7. Eri timeframe
python main.py --analyze BTC/USDT --timeframe 1d
```

Kaikkien pitäisi toimia! 🎉

---

## Suorituskyky

**Demo-moodi:**
- Aika: ~10 sekuntia
- Muisti: ~100 MB
- CPU: Kevyt

**Oikealla datalla:**
- Analyysi: ~3-5 sekuntia per symboli
- Brief: ~15-20 sekuntia (koko watchlist)
- Scan: ~20-30 sekuntia (5 symbolia)

**Kaavio-generointi:**
- +2-3 sekuntia per kaavio
- Tallentuu: charts/ -kansioon

---

## Debug-moodi

Jos jotain menee pieleen:

```bash
# Muokkaa .env:
DEBUG_MODE=True

# Aja uudelleen:
python main.py --analyze BTC/USDT
```

Näyttää yksityiskohtaiset virheviestit.

---

## Tuki

**Toimii?** ✅
→ Ala käyttää päivittäin!

**Ei toimi?** ❌
→ Tarkista:
1. `python demo.py` (pitää toimia aina)
2. `python main.py --config` (tarkista yhteydet)
3. `.env` tiedosto (API-avaimet oikein?)

**Vieläkin ongelmia?**
→ Katso `DEMO_RESULTS.md` ja `README.md`

---

## 🐺 Seuraavat Vaiheet

Kun demo toimii:

1. **Lisää API-avaimet** → Oikea data käyttöön
2. **Ala seurata päivittäin** → 10 min rutiini
3. **Opi tunnistamaan kuvioita** → 2-4 viikkoa
4. **Aloita paper trading** → Harjoittelu
5. **Live trading pienillä summilla** → Kun luottamus riittää

**Muista:**
> Survival > Profit. Understanding > Speed.

🐺 **Trade like a wolf, not a sheep!**
