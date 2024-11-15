from shiny import App, ui, render, reactive
import asyncio

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
                        "CALC05.swf": "Calculus",
                        "TRIG05.swf": "Trigonometry",
                        "LK05.swf": "Linear Kinematics",
                        "FR05.swf": "Force Resolution",
                        "IM05.swf": "Impulse Momentum",
                        "FRIC05.swf": "Friction",
                        "PM.swf": "Projectile Motion",
                        "AK05.swf": "Angular Kinematics",
                        "GK05.swf": "General Kinematics",
                        "TOR05.swf": "Torque/Moment of Force",
                        "MI05.swf": "Moment of Inertia",
                        "SE05.swf": "Static Equilibrium",
                        "DE05.swf": "Dynamics",
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
        # Load Ruffle from jsDelivr CDN instead
        ui.tags.script({"src": "https://cdn.jsdelivr.net/npm/@ruffle-rs/ruffle", "crossorigin": "anonymous"}),
        ui.tags.style("""
            /* Styles remain the same */
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
            window.loadSWF = async function(swf_url) {
                console.log("loadSWF called with URL:", swf_url);
                
                try {
                    const container = document.getElementById("swf-player");
                    if (!container) {
                        throw new Error("SWF container not found");
                    }
                    
                    container.innerHTML = '';
                    
                    if (!swf_url) {
                        container.innerHTML = '<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">Select a topic to load content</div>';
                        return;
                    }
                    
                    // Wait for Ruffle with a timeout
                    const waitForRuffle = async (timeout = 5000) => {
                        const start = Date.now();
                        
                        while (!window.RufflePlayer && (Date.now() - start < timeout)) {
                            await new Promise(resolve => setTimeout(resolve, 100));
                        }
                        
                        if (!window.RufflePlayer) {
                            throw new Error("Ruffle failed to load within " + timeout + "ms");
                        }
                        
                        return window.RufflePlayer.newest();
                    };
                    
                    const ruffle = await waitForRuffle();
                    const player = ruffle.createPlayer();
                    
                    Object.assign(player.style, {
                        position: 'absolute',
                        width: '100%',
                        height: '100%',
                        top: '0',
                        left: '0',
                        visibility: 'visible'
                    });
                    
                    container.appendChild(player);
                    
                    // Add load and error handlers
                    player.addEventListener('loadeddata', () => {
                        console.log('SWF loaded data');
                        player.style.visibility = 'visible';
                    });
                    
                    player.addEventListener('error', (e) => {
                        console.error('SWF error:', e);
                        throw e;
                    });
                    
                    // Test URL availability before loading
                    try {
                        const response = await fetch(swf_url, { method: 'HEAD' });
                        if (!response.ok) {
                            throw new Error(`SWF file not found (${response.status})`);
                        }
                    } catch (error) {
                        throw new Error(`Failed to access SWF file: ${error.message}`);
                    }
                    
                    // Load the SWF with cache busting
                    const cacheBustUrl = `${swf_url}?_=${Date.now()}`;
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
                                <div style="color: #666; font-size: 0.9em;">Please verify that the content exists and try refreshing the page.</div>
                            </div>`;
                    }
                }
            };

            // Add custom message handler
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
            # Change to raw.githubusercontent.com URL
            swf_url = f"https://raw.githubusercontent.com/mklimstra/Biomech-tutor/main/swf/{encoded_file}"
            print(f"Loading SWF from URL: {swf_url}")
            await session.send_custom_message("loadSWF", swf_url)
        else:
            await session.send_custom_message("loadSWF", "")

app = App(app_ui, server)
