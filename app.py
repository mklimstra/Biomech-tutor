from shiny import App, ui, render, reactive
import asyncio
from time import time

app_ui = ui.page_fluid(
    ui.div(
        {"class": "header-container"},
        ui.div(
            {"class": "header-content"},
            ui.h2("Biomechanics Tutor", class_="main-header"),
            ui.div(
                {"class": "selector-container"},
                ui.input_select(
                    "swf_file",
                    None,
                    {
                        "": "Select Topic",
                        "BM05.swf": "Basic Math",
                        "PM.swf": "Projectile Motion",
                    },
                    selected=""
                ),
            ),
        ),
    ),
    ui.row(
        ui.column(12,
            ui.output_ui("swf_container"),
        )
    ),
    ui.tags.head(
        ui.tags.meta({"http-equiv": "Cache-Control", "content": "no-cache, no-store, must-revalidate"}),
        ui.tags.meta({"http-equiv": "Pragma", "content": "no-cache"}),
        ui.tags.meta({"http-equiv": "Expires", "content": "0"}),
        ui.tags.style("""
            .header-container {
                background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
                padding: 8px 16px;
                margin-bottom: 10px;
                border-radius: 6px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                height: 60px;
                max-width: 1600px;
                margin: 0 auto;
                width: calc(100% - 32px);
            }
            
            .header-content {
                display: flex;
                align-items: center;
                height: 100%;
                gap: 30px;
            }
            
            .main-header {
                color: #333333;
                margin: 0;
                font-size: 1.75em;
                font-weight: 600;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            }
            
            .selector-container {
                flex-grow: 1;
                max-width: 300px;
            }
            
            .form-group {
                margin-bottom: 0 !important;
            }
            
            .swf-container {
                width: calc(100% - 32px);
                max-width: 1600px;
                margin: 20px auto;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            
            .swf-aspect-ratio {
                position: relative;
                padding-bottom: 75%;
                height: 0;
                overflow: hidden;
                border-radius: 6px;
            }
            
            #swf-player {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: white;
            }
            
            #swf-player ruffle-player {
                width: 100%;
                height: 100%;
                display: block;
            }
            
            @media (max-width: 768px) {
                .header-container {
                    height: auto;
                    padding: 10px;
                }
                
                .header-content {
                    flex-direction: column;
                    gap: 10px;
                    align-items: stretch;
                }
                
                .selector-container {
                    max-width: none;
                }
            }
        """),
        ui.tags.script("""
            // Load Ruffle with explicit WASM handling
            async function loadRuffle() {
                try {
                    const ruffleScript = document.createElement('script');
                    ruffleScript.src = 'https://unpkg.com/@ruffle-rs/ruffle';
                    ruffleScript.setAttribute('crossorigin', 'anonymous');
                    
                    // Create a promise to wait for the script to load
                    const loadPromise = new Promise((resolve, reject) => {
                        ruffleScript.onload = () => resolve();
                        ruffleScript.onerror = () => reject(new Error('Failed to load Ruffle script'));
                    });
                    
                    document.head.appendChild(ruffleScript);
                    await loadPromise;
                    
                    // Wait for WASM to be available
                    const maxAttempts = 50;
                    let attempts = 0;
                    
                    while (!window.RufflePlayer?.newest() && attempts < maxAttempts) {
                        await new Promise(resolve => setTimeout(resolve, 100));
                        attempts++;
                    }
                    
                    if (!window.RufflePlayer?.newest()) {
                        throw new Error('Ruffle WASM failed to initialize');
                    }
                    
                    console.log('Ruffle loaded successfully');
                    window.ruffleLoaded = true;
                } catch (error) {
                    console.error('Error loading Ruffle:', error);
                    throw error;
                }
            }
            
            // Load Ruffle immediately
            loadRuffle().catch(console.error);
        """),
        ui.tags.script("""
            window.loadSWF = async function(swf_url) {
                console.log("loadSWF called with URL:", swf_url);
                
                try {
                    if (!window.ruffleLoaded) {
                        await loadRuffle();
                    }
                    
                    const container = document.getElementById("swf-player");
                    if (!container) {
                        throw new Error("SWF container not found");
                    }
                    
                    container.innerHTML = '';
                    
                    if (!swf_url) {
                        container.innerHTML = '<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">Select a topic to load content</div>';
                        return;
                    }
                    
                    const ruffle = window.RufflePlayer.newest();
                    const player = ruffle.createPlayer();
                    
                    Object.assign(player.style, {
                        position: 'absolute',
                        width: '100%',
                        height: '100%',
                        top: '0',
                        left: '0'
                    });
                    
                    container.appendChild(player);
                    
                    player.addEventListener('loadeddata', () => console.log('SWF loaded data'));
                    player.addEventListener('error', (e) => {
                        console.error('SWF error:', e);
                        throw e;
                    });
                    
                    const cacheBustUrl = `${swf_url}?_=${new Date().getTime()}`;
                    
                    await player.load({
                        url: cacheBustUrl,
                        allowScriptAccess: true,
                        backgroundColor: "#FFFFFF",
                        scale: "showall",
                        quality: "high",
                        wmode: "direct",
                        menu: true,
                        allowNetworking: "all"
                    });
                    
                    console.log("SWF loaded successfully");
                    
                } catch (error) {
                    console.error("Error in loadSWF:", error);
                    const container = document.getElementById("swf-player");
                    if (container) {
                        container.innerHTML = `
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                <div style="color: red; padding: 20px;">Error loading content: ${error.message}</div>
                                <div style="color: #666; font-size: 0.9em;">Try refreshing the page if the content doesn't load.</div>
                            </div>`;
                    }
                }
            };

            Shiny.addCustomMessageHandler("loadSWF", function(swf_url) {
                window.loadSWF(swf_url);
            });
        """)
    )
)

def server(input, output, session):
    @render.ui
    def swf_container():
        return ui.HTML("""
            <div class="swf-container">
                <div class="swf-aspect-ratio">
                    <div id="swf-player">
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                            Select a topic to load content
                        </div>
                    </div>
                </div>
            </div>
        """)

    @reactive.effect
    @reactive.event(input.swf_file)
    async def _():
        swf_file = input.swf_file()
        if swf_file:
            from urllib.parse import quote
            encoded_file = quote(swf_file)
            swf_url = f"https://mklimstra.github.io/Biomech-tutor/swf/{encoded_file}"
            print(f"Loading SWF from URL: {swf_url}")
            await session.send_custom_message("loadSWF", swf_url)
        else:
            await session.send_custom_message("loadSWF", "")

app = App(app_ui, server)
