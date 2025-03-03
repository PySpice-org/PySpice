import anywidget
import traitlets
import json
import time
from collections import defaultdict

class AnimatedFnWidget(anywidget.AnyWidget):
    # Trait for sending new data points to JavaScript
    new_data_points = traitlets.Unicode('{}').tag(sync=True)
    
    # Trait for initial configuration
    config = traitlets.Unicode('{"xMin": 0, "xMax": 10, "yMin": -1.5, "yMax": 1.5, "series": {}}').tag(sync=True)
    
    _esm = """
    function render({ model, el }) {
    const container = document.createElement('div');
    container.style.width = '100%';
    container.style.height = '400px';
    container.style.border = '1px solid #ccc';
    container.style.position = 'relative';
    el.appendChild(container);
    
    const canvas = document.createElement('canvas');
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    container.appendChild(canvas);
    
    function resizeCanvas() {
        const rect = container.getBoundingClientRect();
        canvas.width = rect.width * window.devicePixelRatio;
        canvas.height = rect.height * window.devicePixelRatio;
        redrawPlot();
    }
    
    window.addEventListener('resize', resizeCanvas);
    
    let allData = {};
    let config = JSON.parse(model.get('config'));
    const colors = ['#3498db', '#e74c3c', '#2ecc71', '#9b59b6', '#f1c40f', '#e67e22'];
    
    model.on('change:config', () => {
        config = JSON.parse(model.get('config'));
        allData = {};
        Object.keys(config.series).forEach(series => {
            allData[series] = { x: [], y: [] };
        });
        redrawPlot();
    });
    
    model.on('change:new_data_points', () => {
        const newData = JSON.parse(model.get('new_data_points'));
        if (Object.keys(newData).length === 0) return;
        
        Object.entries(newData).forEach(([series, points]) => {
            if (!allData[series]) {
                allData[series] = { x: [], y: [] };
            }
            allData[series].x = allData[series].x.concat(points.x);
            allData[series].y = allData[series].y.concat(points.y);
            
            if (allData[series].x.length > 0) {
                const maxX = Math.max(...Object.values(allData).map(d => Math.max(...d.x)));
                if (maxX > config.xMax) {
                    config.xMin = Math.max(0, maxX - 10);
                    config.xMax = maxX;
                }
            }
        });
        
        redrawPlot();
    });
    
    function redrawPlot() {
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Compute yMin and yMax dynamically if not specified
        let yMin, yMax;
        if (typeof config.yMin === 'number' && typeof config.yMax === 'number') {
            yMin = config.yMin;
            yMax = config.yMax;
        } else {
            // Auto-scale y-axis
            let allYValues = [];
            Object.values(allData).forEach(series => {
                allYValues = allYValues.concat(series.y);
            });
            if (allYValues.length === 0) {
                yMin = -1;
                yMax = 1;
            } else {
                let dataMin = Math.min(...allYValues);
                let dataMax = Math.max(...allYValues);
                if (dataMin === dataMax) {
                    yMin = dataMin - 1;
                    yMax = dataMax + 1;
                } else {
                    let padding = (dataMax - dataMin) * 0.1;
                    yMin = dataMin - padding;
                    yMax = dataMax + padding;
                }
            }
        }
        
        ctx.clearRect(0, 0, width, height);
        
        // Draw grid
        ctx.strokeStyle = '#ccc';
        ctx.lineWidth = 1 * window.devicePixelRatio;
        ctx.beginPath();
        const gridStep = width / 10;
        for (let i = 0; i <= 10; i++) {
            const x = i * gridStep;
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
        }
        const yGridStep = height / 6;
        for (let i = 0; i <= 6; i++) {
            const y = i * yGridStep;
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
        }
        ctx.stroke();
        
        // Draw axes
        ctx.strokeStyle = '#000';
        const yZero = height * (1 - (0 - yMin) / (yMax - yMin));
        ctx.beginPath();
        ctx.moveTo(0, yZero);
        ctx.lineTo(width, yZero);
        ctx.stroke();
        
        const xZero = width * (0 - config.xMin) / (config.xMax - config.xMin);
        ctx.beginPath();
        ctx.moveTo(xZero, 0);
        ctx.lineTo(xZero, height);
        ctx.stroke();
        
        function dataToCanvas(x, y) {
            return {
                x: width * (x - config.xMin) / (config.xMax - config.xMin),
                y: height * (1 - (y - yMin) / (yMax - yMin))
            };
        }
        
        // Draw all series (no config.series check)
        Object.entries(allData).forEach(([series, data], index) => {
            if (data.x.length > 1) {
                const visibleData = data.x.map((x, i) => ({x, y: data.y[i]}))
                    .filter(point => point.x >= config.xMin && point.x <= config.xMax);
                
                if (visibleData.length > 0) {
                    ctx.beginPath();
                    const startPoint = dataToCanvas(visibleData[0].x, visibleData[0].y);
                    ctx.moveTo(startPoint.x, startPoint.y);
                    
                    for (let i = 1; i < visibleData.length; i++) {
                        const point = dataToCanvas(visibleData[i].x, visibleData[i].y);
                        ctx.lineTo(point.x, point.y);
                    }
                    
                    ctx.strokeStyle = colors[index % colors.length];
                    ctx.lineWidth = 2 * window.devicePixelRatio;
                    ctx.stroke();
                    
                    // Draw legend with fallback label
                    ctx.fillStyle = colors[index % colors.length];
                    ctx.fillRect(10, 10 + index * 20, 10, 10);
                    ctx.fillStyle = '#000';
                    ctx.font = `${12 * window.devicePixelRatio}px Arial`;
                    const label = config.series[series] ? config.series[series].label : series;
                    ctx.fillText(label, 25, 20 + index * 20);
                }
            }
        });
        
        // Draw axes labels
        ctx.fillStyle = '#000';
        ctx.font = `${12 * window.devicePixelRatio}px Arial`;
        ctx.fillText(`t`, width - 15, yZero - 5);
        ctx.fillText(`${config.xMin.toFixed(1)}`, 5, yZero - 5);
        ctx.fillText(`${config.xMax.toFixed(1)}`, width - 30, yZero - 5);
        ctx.fillText(`${yMax.toFixed(1)}`, xZero + 5, 15);
        ctx.fillText(`${yMin.toFixed(1)}`, xZero + 5, height - 5);
    }
    
    setTimeout(resizeCanvas, 0);
}

export default { render };
    """

    def __init__(self, update_interval_ms=100, **kwargs):
        super().__init__(**kwargs)
        self.update_interval = update_interval_ms / 1000
        self.last_update_time = 0
        self.buffer = defaultdict(lambda: {'x': [], 'y': []})
        
    def update_config(self, config_dict):
        """Update the plot configuration"""
        self.config = json.dumps(config_dict)
        
    def add_points(self, series_name, x_values, y_values):
        """Add points for a specific series"""
        if len(x_values) != len(y_values):
            raise ValueError("x_values and y_values must have the same length")
            
        self.buffer[series_name]['x'].extend(x_values)
        self.buffer[series_name]['y'].extend(y_values)
        
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            self._flush_buffer()
            self.last_update_time = current_time
            
    def _flush_buffer(self):
        """Send buffered data to JavaScript"""
        if not self.buffer:
            return
            
        self.new_data_points = json.dumps(dict(self.buffer))
        for series in self.buffer:
            self.buffer[series]['x'].clear()
            self.buffer[series]['y'].clear()

# Example usage with sine wave
def test_sine_wave(widget):
    import numpy as np
    config = {
        "xMin": 0,
        "xMax": 10,
        "yMin": -1.5,
        "yMax": 1.5,
        "series": {
            "sine": {"label": "Sine Wave"}
        }
    }
    widget.update_config(config)
    
    t = 0
    dt = 0.05
    points_per_update = 5
    
    while t < 20:
        x_values = [t + i * dt for i in range(points_per_update)]
        y_values = [np.sin(2 * np.pi * x) for x in x_values]
        widget.add_points("sine", x_values, y_values)
        t += dt * points_per_update
        time.sleep(widget.update_interval)


# -

anim_widget = AnimatedFnWidget(update_interval_ms=100)
anim_widget

test_sine_wave(anim_widget) #if this doesn't work then forget it

# +
from PySpice.Spice.Netlist import Circuit
from PySpice import SpiceLibrary, Circuit, Simulator, plot
from PySpice.Unit import *

# Create a circuit
circuit = Circuit('My Circuit')

# Add components to the circuit
circuit.R('res1', 'k', 'y', 1@u_Ω)  # Resistor R1 between nodes 'k' and 'y' with 1 Ω
circuit.C('cap1', 0, 'k', 1@u_F, ic=0.0)  # Capacitor C1 between nodes 0 and 'k' with 1 F, initial condition 0.0
circuit.V('vdc', 0, 'y', 1@u_V)  # Voltage source V1 between nodes 0 and 'y' with 1 V

# Print the circuit to verify
print(circuit)

# -

def couple_with_ngspice(widget, simulator, start, end, step, y_range=(-2, 2)):
    """
    Couple the AnimatedFnWidget with an NGSpice simulation, plotting all available signals.
    
    Args:
        widget: AnimatedFnWidget instance
        simulator: PySpice simulator object
        start: Simulation start time
        end: Simulation end time
        step: Simulation time step
        y_range: Tuple of (min, max) values for y-axis
    """
    # Initial config with empty series; labels will use signal names
    config = {
        "xMin": start,
        "xMax": end,
        "yMin": y_range[0],
        "yMax": y_range[1],
        "series": {}
    }
    widget.update_config(config)
    
    def data_listener(actual_vector_values, number_of_vectors, ngspice_id):
        time_value = float(actual_vector_values['time'].real)
        for signal, value in actual_vector_values.items():
            if signal != 'time':
                widget.add_points(signal, [time_value], [float(value.real)])
    
    simulator.simulator._ngspice_shared.addListener("send_data", data_listener)
    # display(widget)
    simulator.transient(step, end, start, use_initial_condition=True, background=True)


# +
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from PySpice.Spice.NgSpice.Shared import NgSpiceShared
class MyNgSpiceShared(NgSpiceShared):
    def __init__(self, ngspice_id=0, send_data=False, verbose=False):
        super().__init__(ngspice_id=ngspice_id, send_data=send_data, verbose=verbose)
        self._listeners = {
            "send_data": [],
            "send_init_data": []
        }

    def addListener(self, event, listener):
        if event in self._listeners:
            self._listeners[event].append(listener)
        else:
            raise ValueError(f"Ev'ent '{event}' is not supported.")

    def removeListener(self, event, listener):
        if event in self._listeners:
            if listener in self._listeners[event]:
                self._listeners[event].remove(listener)
            else:
                raise ValueError(f"Listener '{listener.__name__}' is not registered for event '{event}'.")
        else:
            raise ValueError(f"Event '{event}' is not supported.")

    def _notify_listeners(self, event, *args, **kwargs):
        if event in self._listeners:
            for listener in self._listeners[event]:
                listener(*args, **kwargs)

    def send_data(self, actual_vector_values, number_of_vectors, ngspice_id):
        # Notify listeners for the 'send_data' event
        self._notify_listeners("send_data", actual_vector_values, number_of_vectors, ngspice_id)
        return 0

    def send_init_data(self, data, ngspice_id):
        # Notify listeners for the 'send_init_data' event
        self._notify_listeners("send_init_data", data, ngspice_id)
        return 0



ngshared = MyNgSpiceShared.new_instance(send_data=True,ngspice_id=0)
simulator =Simulator.factory().simulation(circuit,temperature=25, nominal_temperature=25
                             ,ngspice_shared=MyNgSpiceShared.new_instance(send_data=True)
                             )
analysis = simulator.dc(Vvdc=slice(-2, 5, .01))

# simulator = circuit.simulator(
#     temperature=25,
#     nominal_temperature=25,
#     ngspice_shared=MyNgSpiceShared.new_instance(send_data=True)
# )
anim_widget = AnimatedFnWidget(update_interval_ms=100)
couple_with_ngspice(anim_widget, simulator, 0, 12, 0.0001)# If your computer is too fast make this smaller.... if your computer is too slow make this bigger.
# -
simulator.simulator._ngspice_shared.halt() ## Execute these instructions when they are on the middle.

simulator.simulator._ngspice_shared.alter_device(device='Vvdc', dc=-1)


simulator.simulator._ngspice_shared.resume()