# 🚀 Bytt til X11 for Full AIKI Autonomi

## Hvorfor X11?
Wayland blokkerer screenshot og GUI automation av sikkerhetsgrunner.
X11 tillater AIKI å:
- ✅ Ta screenshots
- ✅ Lese skjermen (OCR)
- ✅ Klikke knapper automatisk
- ✅ Kontrollere vinduer

## Slik bytter du:

1. **Logg ut nå:**
   - Klikk på strømknappen øverst til høyre
   - Velg "Log Out" / "Logg ut"

2. **Ved innloggingsskjermen:**
   - Skriv inn passord som vanlig
   - **MEN VENT!** Før du trykker Enter/Login:
   - Se etter ⚙️ (tannhjul-ikon) nederst til høyre
   - Klikk på ⚙️
   - Velg **"GNOME on Xorg"** eller **"GNOME X11"**
   - NÅ trykk Enter/Login

3. **Du er tilbake med X11!**
   - Alt ser likt ut
   - Men nå fungerer AIKI autonomi-verktøy!

## Test at det virker:

Når du er logget inn igjen:
```bash
echo $XDG_SESSION_TYPE
```

Skal vise: **x11** (ikke "wayland")

## Start AIKI igjen:

Bare fortsett der vi slapp - Chiaki er allerede konfigurert!

---

**Klar? Logg ut nå og velg X11 ved innlogging! 🎯**
