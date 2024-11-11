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
        ui.tags.script("""
            // Load Ruffle dynamically
            var ruffleScript = document.createElement('script');
            ruffleScript.src = 'https://unpkg.com/@ruffle-rs/ruffle';
            ruffleScript.setAttribute('crossorigin', 'anonymous');
            document.head.appendChild(ruffleScript);
        """),
        ui.tags.style("""
            * {
                -webkit-box-sizing: border-box;
                -moz-box-sizing: border-box;
                box-sizing: border-box;
            }
            
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
                -webkit-box-sizing: border-box;
                box-sizing: border-box;
            }
            
            .header-content {
                display: -webkit-flex;
                display: flex;
                -webkit-align-items: center;
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
                font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
                white-space: nowrap;
                line-height: 1;
                padding-top: 3px;
            }
            
            .selector-container {
                display: -webkit-flex;
                display: flex;
                -webkit-align-items: center;
                align-items: center;
                gap: 12px;
                height: 100%;
            }
            
            .selectInput {
                max-width: 400px;
                min-width: 200px;
            }
            
            .form-group {
                margin-bottom: 0 !important;
            }
            
            .form-control {
                height: 34px !important;
                padding-top: 0 !important;
                padding-bottom: 0 !important;
            }
            
            .swf-container {
                width: calc(100% - 32px);
                max-width: 1600px;
                margin: 20px auto;
                background-color: white;
                border: 2px solid white;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                position: relative;
                -webkit-box-sizing: border-box;
                box-sizing: border-box;
            }
            
            .swf-aspect-ratio {
                position: relative;
                padding-bottom: 75%;
                height: 0;
                overflow: hidden;
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
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: block;
                -webkit-transform: translateZ(0);
                transform: translateZ(0);
            }

            @media (max-width: 768px) {
                .header-container,
                .swf-container {
                    width: calc(100% - 20px);
                }
            }

            @supports (-webkit-overflow-scrolling: touch) {
                #swf-player ruffle-player {
                    -webkit-transform: translateZ(0);
                    transform: translateZ(0);
                    -webkit-backface-visibility: hidden;
                    backface-visibility: hidden;
                }
            }
        """)
    ),
    ui.tags.script("""
    console.log("Script starting...");
    
    window.loadSWF = async function(swf_url) {
        console.log("loadSWF called with URL:", swf_url);
        
        try {
            // More robust Ruffle availability check
            let attempts = 0;
            const maxAttempts = 50;
            
            while ((!window.RufflePlayer || !window.RufflePlayer.newest()) && attempts < maxAttempts) {
                console.log(`Waiting for Ruffle... Attempt ${attempts + 1}`);
                await new Promise(resolve => setTimeout(resolve, 100));
                attempts++;
            }
            
            if (!window.RufflePlayer || !window.RufflePlayer.newest()) {
                throw new Error("Ruffle failed to load after multiple attempts");
            }
            
            const container = document.getElementById("swf-player");
            if (!container) {
                throw new Error("SWF container not found");
            }
            
            // Clear the container
            container.innerHTML = '';
            
            if (!swf_url) {
                container.innerHTML = '<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">Select a topic to load content</div>';
                return;
            }
            
            // Create and configure the player
            const ruffle = window.RufflePlayer.newest();
            const player = ruffle.createPlayer();
            
            // Configure player before loading
            player.style.position = 'absolute';
            player.style.width = '100%';
            player.style.height = '100%';
            player.style.visibility = 'visible';  // Ensure visibility in Safari
            
            // Safari-specific styles
            if (/^((?!chrome|android).)*safari/i.test(navigator.userAgent)) {
                player.style.webkitTransform = 'translateZ(0)';
                player.style.webkitBackfaceVisibility = 'hidden';
            }
            
            container.appendChild(player);
            
            // Add event listeners
            player.addEventListener('loadeddata', () => {
                console.log('SWF loaded data');
                player.style.visibility = 'visible';
            });
            
            player.addEventListener('playing', () => console.log('SWF is playing'));
            
            player.addEventListener('error', (e) => {
                console.error('SWF error:', e);
                throw e;
            });
            
            console.log("Loading SWF...");
            
            // Load the SWF with specific configuration
            await player.load({
                url: swf_url,
                allowScriptAccess: true,
                backgroundColor: "#FFFFFF",
                scale: "showall",
                salign: "",
                quality: "high",
                wmode: "direct",
                menu: true,
                base: new URL(swf_url).origin + "/",
                allowNetworking: "all",
                letterbox: "on"
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
    
    // Improved resize handler
    window.addEventListener('resize', function() {
        const player = document.querySelector('ruffle-player');
        if (player) {
            player.style.webkitTransform = 'translateZ(0)';
            player.style.transform = 'translateZ(0)';
        }
    });
    """)
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
