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
        ui.tags.script(src="https://unpkg.com/@ruffle-rs/ruffle"),
    ),
    ui.tags.style("""
        .header-container {
            background: linear-gradient(135deg, #f5f5f5, #e0e0e0);
            padding: 8px 16px;
            margin-bottom: 10px;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            height: 60px;
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
            font-family: 'Helvetica Neue', Arial, sans-serif;
            white-space: nowrap;
            line-height: 1;
            padding-top: 3px;
        }
        
        .selector-container {
            display: flex;
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
        
        #swf-player {
            width: 800px;  /* Fixed width */
            height: 600px; /* Fixed height */
            background-color: white;
            margin: 20px auto;
            border: 1px solid #ccc;
            position: relative;
        }
        
        #swf-player ruffle-player {
            position: absolute !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 100% !important;
            display: block !important;
        }
    """),
    ui.tags.script("""
    console.log("Script starting...");
    
    window.loadSWF = async function(swf_url) {
        console.log("loadSWF called with URL:", swf_url);
        
        try {
            // Wait for Ruffle to be available
            while (!window.RufflePlayer || !window.RufflePlayer.newest()) {
                console.log("Waiting for Ruffle...");
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            const container = document.getElementById("swf-player");
            if (!container) {
                throw new Error("SWF container not found");
            }
            
            // Clear the container
            container.innerHTML = '';
            
            if (!swf_url) {
                return;
            }
            
            // Create and configure the player
            const ruffle = window.RufflePlayer.newest();
            const player = ruffle.createPlayer();
            container.appendChild(player);
            
            // Add debug listener for player events
            player.addEventListener('loadeddata', () => console.log('SWF loaded data'));
            player.addEventListener('playing', () => console.log('SWF is playing'));
            player.addEventListener('error', (e) => console.error('SWF error:', e));
            
            console.log("Loading SWF...");
            
            // Load the SWF with specific configuration
            await player.load({
                url: swf_url,
                allowScriptAccess: true,
                backgroundColor: "#FFFFFF",
                scale: "noborder",
                salign: "",
                quality: "high",
                wmode: "direct",
                menu: true,
                base: new URL(swf_url).origin + "/",
                allowNetworking: "all"
            });
            
            console.log("SWF loaded successfully");
            console.log("Player dimensions:", player.offsetWidth, "x", player.offsetHeight);
            
        } catch (error) {
            console.error("Error in loadSWF:", error);
            const container = document.getElementById("swf-player");
            if (container) {
                container.innerHTML = `<div style="color: red; padding: 20px;">Error loading SWF: ${error.message}</div>`;
            }
        }
    };

    // Register the custom message handler
    Shiny.addCustomMessageHandler("loadSWF", function(swf_url) {
        window.loadSWF(swf_url);
    });
    
    console.log("Script initialization complete");
    """),
)

def server(input, output, session):
    @render.ui
    def swf_container():
        return ui.HTML("""
            <div id='swf-player'>
                <div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);'>
                    Select a topic to load content
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
            print(f"Loading SWF from URL: {swf_url}")  # Server-side debug print
            await session.send_custom_message("loadSWF", swf_url)
        else:
            await session.send_custom_message("loadSWF", "")

app = App(app_ui, server)
