from shiny import App, ui, render, reactive
import asyncio

app_ui = ui.page_fluid(
    ui.tags.head(
        # Include Ruffle script from the CDN
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/ruffle-nightly@latest/ruffle.js"),
    ),
    ui.h2("ShinyLive Ruffle Integration"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "swf_file",
                "Select SWF File",
                {
                    "PM.swf": "PM",
                    # Add more SWF files here if needed
                },
            ),
            ui.input_action_button("load_swf", "Load SWF"),
        ),
            ui.output_ui("swf_container")
    ),
    # Inject JavaScript code to initialize Ruffle
    ui.tags.script("""
    window.loadSWF = async function(swf_url) {
        // Wait for Ruffle to be ready
        if (!window.rufflePlayer) {
            await new Promise((resolve) => {
                const checkRuffle = setInterval(() => {
                    if (window.RufflePlayer) {
                        window.rufflePlayer = window.RufflePlayer.newest();
                        clearInterval(checkRuffle);
                        resolve();
                    }
                }, 100);
            });
        }
        
        console.log("loadSWF called with URL:", swf_url);
        if (window.player) {
            window.player.remove();
        }
        const container = document.getElementById("swf-player");
        window.player = window.rufflePlayer.createPlayer();
        container.appendChild(window.player);
        window.player.load(swf_url);
    };

    // Add Shiny message handler
    Shiny.addCustomMessageHandler("loadSWF", function(swf_url) {
        window.loadSWF(swf_url);
    });
    """),
)

def server(input, output, session):
    @render.ui
    def swf_container():
        return ui.HTML("<div id='swf-player'></div>")

    @reactive.effect
    @reactive.event(input.load_swf)
    async def _():
        swf_file = input.swf_file()
        from urllib.parse import quote
        encoded_file = quote(swf_file)
        swf_url = f"./swf/{encoded_file}"
        await session.send_custom_message("loadSWF", swf_url)

app = App(app_ui, server)
