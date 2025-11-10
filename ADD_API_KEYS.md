# 🔑 API-avainten lisääminen

## Binance API (Markkinadata)

### 1. Hanki API-avaimet

1. **Kirjaudu Binanceen:** https://www.binance.com
2. **Mene API Management:**
   - Klikkaa profiilikuvaa (oikeassa yläkulmassa)
   - Valitse "API Management"
3. **Luo uusi API Key:**
   - Label: "Wolf Market Analyzer"
   - Restrictions: ✓ **Enable Reading** (VAIN lukuoikeus!)
   - ❌ **ÄLÄ** aktivoi trading-oikeuksia!
4. **IP Whitelist** (suositeltu):
   - Lisää IP-osoitteesi lisäturvallisuuden vuoksi
   - Tai jätä tyhjäksi jos IP muuttuu usein
5. **Kopioi avaimet:**
   - API Key (pitkä merkkijono)
   - Secret Key (näytetään vain kerran - kopioi heti!)

### 2. Lisää .env-tiedostoon

```bash
cd /home/user/Trading-App
nano .env
```

Päivitä nämä rivit:
```bash
BINANCE_API_KEY=paste_your_api_key_here
BINANCE_API_SECRET=paste_your_secret_key_here
```

Tallenna: `Ctrl+O`, `Enter`, `Ctrl+X`

### 3. Testaa yhteys

```bash
source venv/bin/activate
python main.py --config
```

Pitäisi näyttää:
```
Binance API: ✓ Connected
```

---

## Anthropic Claude API (AI-analyysi)

### 1. Hanki API-avain

1. **Mene:** https://console.anthropic.com
2. **Luo tili** (jos ei ole)
3. **Valitse:** "API Keys"
4. **Luo:** "Create Key"
5. **Kopioi** avain (alkaa: sk-ant-...)

### 2. Lisää .env-tiedostoon

```bash
nano .env
```

Päivitä:
```bash
ANTHROPIC_API_KEY=sk-ant-your_actual_key_here
```

### 3. Testaa

```bash
python main.py --config
```

Pitäisi näyttää:
```
Claude AI: ✓ Connected
```

---

## 🎯 Kun molemmat API:t on konfiguroitu

### Testaa täydellä toiminnallisuudella:

```bash
# Analysoi Bitcoin
python main.py --analyze BTC/USDT

# Päivittäinen briefing
python main.py --brief

# Skannaa watchlist
python main.py --scan
```

Nyt saat:
- ✅ Oikeat markkinadatan (Binance)
- ✅ AI-analyysit (Claude)
- ✅ Kaaviot entry/stop/target -tasoilla
- ✅ Institutionaalisen käyttäytymisen selitykset

---

## 💰 Kustannukset

### Binance API
- **Ilmainen** (read-only)
- Ei kustannuksia datan haussa
- Ei vaadi kaupankäyntiä

### Anthropic Claude API
- **$3-5 / kuukausi** (tyypillinen käyttö)
- Ensimmäiset $5 ilmaiseksi (new users)
- Maksut perustuvat API-kutsuihin

**Arvio päivittäiselle käytölle:**
- Morning brief: ~$0.02
- 2-3 analyysiä: ~$0.05
- Yhteensä: **~$2-3 / kuukausi**

---

## 🔒 Turvallisuus

### ✅ DO:
- Käytä vain "Read" -oikeutta Binancessa
- Pidä avaimet .env-tiedostossa (ei Git!)
- Aktivoi IP whitelist jos mahdollista
- Vaihda avaimet jos epäilet vuotoa

### ❌ DON'T:
- **ÄLÄ** anna trading-oikeuksia
- **ÄLÄ** jaa avaimia kenellekään
- **ÄLÄ** commitoi .env-tiedostoa Gitiin
- **ÄLÄ** käytä samoja avaimia trading-botille

---

## 🧪 Testaa ilman API-avaimia

Jos et halua vielä lisätä API-avaimia:

```bash
python demo.py
```

Tämä toimii täysin ilman avaimia ja näyttää kaikki ominaisuudet!

---

## ❓ Ongelmat?

### "Binance API error"
- Tarkista että avain on oikein
- Varmista että "Enable Reading" on päällä
- Tarkista IP whitelist -asetukset

### "Claude AI error"
- Tarkista avain (alkaa: sk-ant-)
- Varmista että sinulla on credittiä
- Kokeile: https://console.anthropic.com

### "Permission denied"
- Binance API:ssa ei ole trading-oikeutta (hyvä!)
- Käytä vain "Enable Reading"

---

**Kun API:t on konfiguroitu, sovellus toimii täydellä teholla!** 🚀
