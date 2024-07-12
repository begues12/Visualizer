from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

class WebControlPanel:
    def __init__(self, visualizer):
        self.visualizer = visualizer
        self.app = app
        self.setup_routes()

    def run(self):
        self.app.run(debug=True)

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html', effects=self.get_effects())

        @self.app.route('/change_effect', methods=['POST'])
        def change_effect():
            effect_name = request.form.get('effect')
            self.visualizer.change_current_effect(effect_name)
            return redirect(url_for('index'))

        @self.app.route('/update_config', methods=['POST'])
        def update_config():
            effect_name = request.form.get('effect')
            config = {key: request.form.get(key) for key in request.form if key != 'effect'}
            self.visualizer.update_effect_config(effect_name, config)
            return redirect(url_for('index'))

    def get_effects(self):
        return [effect.get_effect_name() for effect in self.visualizer.drawing_functions]

# Crear instancias de las clases necesarias y correr el servidor
if __name__ == '__main__':
    visualizer = Visualizer()  # Deberías definir tu propia clase Visualizer o adaptarla
    web_control_panel = WebControlPanel(visualizer)
    web_control_panel.run()
