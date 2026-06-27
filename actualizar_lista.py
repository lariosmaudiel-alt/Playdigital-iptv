import re
import time
from playwright.sync_api import sync_playwright

def extraer_con_playwright(url_web):
    enlace_m3u8 = None
    print(f"🌐 Abriendo navegador virtual para: {url_web}")
    
    with sync_playwright() as p:
        # Lanzar Chrome en modo oculto (headless) con un perfil de usuario común
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Función interna que revisa cada petición de red que hace la página (Igual al F12)
        def interceptar_peticion(request):
            nonlocal enlace_m3u8
            url = request.url
            if ".m3u8" in url and not enlace_m3u8:
                # Filtrar solo el enlace principal de video (evitando sub-calidades repetidas)
                if "mono" in url or "playlist" in url or "index" in url or "stream" in url or "token" in url:
                    enlace_m3u8 = url
                    print(f"🎯 ¡Enlace capturado en la red!: {enlace_m3u8}")

        # Escuchar el tráfico de red
        page.on("request", interceptar_peticion)
        
        try:
            # Ir a la página web esperando hasta 30 segundos a que cargue el reproductor
            page.goto(url_web, wait_until="networkidle", timeout=30000)
            
            # Esperar 5 segundos extra para que los scripts internos de video se ejecuten
            time.sleep(5)
            
        except Exception as e:
            print(f"⚠️ Nota de carga en {url_web}: {e}")
        finally:
            context.close()
            browser.close()
            
    return enlace_m3u8

# =========================================================================
# TU SECCIÓN DE CANALES MIXTOS
# =========================================================================

# 1. Canales Directos (No necesitan extractor, van fijos)
canales_directos = {
    "HCH En Vivo": "https://live.streamhch.com/live/streams/hch1.m3u8",
    "HCH Alternativo": "https://hch.tv/live/hch/playlist.m3u8"
}

# 2. Canales dinámicos (Playwright entrará a la web a cazar el .m3u8 del F12)
canales_dinamicos = {
    "DSports": "https://tvlibre-online.com/en-vivo/dsports/",
    "DSports HD": "https://www.telegratishd.com/directv-sports-en-vivo.php"
}

# =========================================================================

print("Generando tu lista IPTV automatizada con Playwright...")
with open("lista_automatica.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    
    # Escribir canales directos
    for nombre, url_directa in canales_directos.items():
        f.write(f'#EXTINF:-1, {nombre}\n')
        f.write(f'{url_directa}\n')
        print(f"✅ Canal directo agregado: {nombre}")
        
    # Escribir canales cazados en vivo
    for nombre, url_web in canales_dinamicos.items():
        url_capturada = extraer_con_playwright(url_web)
        if url_capturada:
            f.write(f'#EXTINF:-1, {nombre}\n')
            # Dejar etiquetas de compatibilidad por si lo abres en VLC
            f.write(f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)\n')
            f.write(f'{url_capturada}\n')
            print(f"✅ Canal extraído con Playwright: {nombre}")
        else:
            print(f"❌ Playwright no pudo cazar el enlace de red para: {nombre}")

print("¡Proceso terminado con éxito!")
