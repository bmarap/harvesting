import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, RadioButtons, Button, TextBox

# --- 1. CONFIGURATION (Biological Parameters) ---
# Same biological model as the original
INITIAL_POP = np.array([1000.0, 500.0, 200.0]) 
F_J, F_S, F_A = 0.0, 0.8, 2.5 
S_J_to_S = 0.5 
S_S_to_A = 0.7
S_A_surv = 0.8  

# --- 2. STATE MANAGEMENT ---
class SimulationState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.current_pop = INITIAL_POP.copy()
        self.history_j = [INITIAL_POP[0]]
        self.history_s = [INITIAL_POP[1]]
        self.history_a = [INITIAL_POP[2]]
        self.history_tot = [np.sum(INITIAL_POP)]
        self.time = [0]
        self.is_running = False
        self.year_counter = 0

    def step(self, val_j, val_s, val_a, mode):
        # Calculate survivors based on harvest mode
        survivors = np.zeros(3)
        current = self.current_pop
        
        if mode == 'Constant Quota':
            survivors[0] = max(0, current[0] - val_j)
            survivors[1] = max(0, current[1] - val_s)
            survivors[2] = max(0, current[2] - val_a)
            
        elif mode == 'Proportional (Uniform)':
            global_rate = val_j 
            survivors = current * (1 - global_rate)
            
        elif mode == 'Selective (Age-Specific)':
            survivors[0] = current[0] * (1 - val_j)
            survivors[1] = current[1] * (1 - val_s)
            survivors[2] = current[2] * (1 - val_a)

        # Biological progression (Matrix multiplication equivalent)
        next_j = (survivors[0] * F_J) + (survivors[1] * F_S) + (survivors[2] * F_A)
        next_s = survivors[0] * S_J_to_S
        next_a = (survivors[1] * S_S_to_A) + (survivors[2] * S_A_surv)
        
        self.current_pop = np.array([next_j, next_s, next_a])
        self.year_counter += 1
        
        # Append to history
        self.history_j.append(next_j)
        self.history_s.append(next_s)
        self.history_a.append(next_a)
        self.history_tot.append(np.sum(self.current_pop))
        self.time.append(self.year_counter)

sim_state = SimulationState()

# --- 3. PLOTTING SETUP ---
fig, ax = plt.subplots(figsize=(14, 7))
plt.subplots_adjust(left=0.1, bottom=0.35, right=0.70) 

# Initial Empty Lines
l_j, = ax.plot([], [], lw=2, label='Juvenile')
l_s, = ax.plot([], [], lw=2, label='Sub-Adult')
l_a, = ax.plot([], [], lw=2, label='Adult')
l_tot, = ax.plot([], [], 'k--', lw=2, label='Total')

ax.set_title("Real-Time Harvesting Monitor (Paused)")
ax.set_xlabel("Time (Years)")
ax.set_ylabel("Population Size")
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 50)
ax.set_ylim(0, 2000)

# --- DISPLAY PARAMETERS TEXT BOX ---
param_text = (
    "BIOLOGICAL PARAMETERS\n"
    "---------------------\n"
    f"Initial Pop:\n"
    f"  J: {INITIAL_POP[0]}\n"
    f"  S: {INITIAL_POP[1]}\n"
    f"  A: {INITIAL_POP[2]}\n\n"
    f"Fecundity (F):\n  J:{F_J} S:{F_S} A:{F_A}\n\n"
    f"Survival (S):\n  J->S:{S_J_to_S}\n  S->A:{S_S_to_A}\n  A->A:{S_A_surv}"
)
fig.text(0.72, 0.60, param_text, fontsize=10, family='monospace', 
         verticalalignment='center', bbox=dict(boxstyle='round', facecolor='whitesmoke', alpha=0.8))

# --- 4. CONTROLS ---
axcolor = 'lightgoldenrodyellow'

# Control Axes
ax_play = plt.axes([0.80, 0.02, 0.10, 0.05])
ax_reset = plt.axes([0.68, 0.02, 0.10, 0.05])
ax_speed = plt.axes([0.15, 0.02, 0.35, 0.03], facecolor=axcolor)

# Harvest Sliders axes
ax_s1 = plt.axes([0.15, 0.20, 0.35, 0.03], facecolor=axcolor)
ax_s2 = plt.axes([0.15, 0.15, 0.35, 0.03], facecolor=axcolor)
ax_s3 = plt.axes([0.15, 0.10, 0.35, 0.03], facecolor=axcolor)

# Text Box axes
ax_t1 = plt.axes([0.55, 0.20, 0.08, 0.03])
ax_t2 = plt.axes([0.55, 0.15, 0.08, 0.03])
ax_t3 = plt.axes([0.55, 0.10, 0.08, 0.03])

# Buttons and Speed Slider
btn_play = Button(ax_play, 'Play/Pause', color=axcolor, hovercolor='0.975')
btn_reset = Button(ax_reset, 'Reset', color=axcolor, hovercolor='0.975')
s_speed = Slider(ax_speed, 'Speed (FPS)', 1, 10, valinit=2, valstep=1)

# Harvest Sliders
s1 = Slider(ax_s1, 'Harvest J', 0.0, 1.0, valinit=0.0)
s2 = Slider(ax_s2, 'Harvest S', 0.0, 1.0, valinit=0.0)
s3 = Slider(ax_s3, 'Harvest A', 0.0, 1.0, valinit=0.0)
s1.valtext.set_visible(False); s2.valtext.set_visible(False); s3.valtext.set_visible(False)

# Text Boxes
t1 = TextBox(ax_t1, '', initial='0.00')
t2 = TextBox(ax_t2, '', initial='0.00')
t3 = TextBox(ax_t3, '', initial='0.00')

# Radio Button
ax_radio = plt.axes([0.72, 0.10, 0.18, 0.15], facecolor=axcolor)
radio = RadioButtons(ax_radio, ('Constant Quota', 'Proportional (Uniform)', 'Selective (Age-Specific)'), active=2)

# --- 5. LOGIC and ANIMATION ---
def update_plot():
    # Update lines
    l_j.set_data(sim_state.time, sim_state.history_j)
    l_s.set_data(sim_state.time, sim_state.history_s)
    l_a.set_data(sim_state.time, sim_state.history_a)
    l_tot.set_data(sim_state.time, sim_state.history_tot)
    
    # Auto-scroll x-axis
    if sim_state.year_counter > 40:
        ax.set_xlim(sim_state.year_counter - 40, sim_state.year_counter + 10)
    else:
        ax.set_xlim(0, 50)
        
    # Auto-scale y-axis
    max_pop = max(200, np.max(sim_state.history_tot))
    ax.set_ylim(0, max_pop * 1.2)
    
    # Update Title
    status = "RUNNING" if sim_state.is_running else "PAUSED"
    ax.set_title(f"Real-Time Harvesting Monitor ({status}) - Year: {sim_state.year_counter}")
    fig.canvas.draw_idle()

def animate(i):
    if not sim_state.is_running:
        return
        
    mode = radio.value_selected
    sim_state.step(s1.val, s2.val, s3.val, mode)
    update_plot()

# Button Callbacks
def toggle_play(event):
    sim_state.is_running = not sim_state.is_running
    update_plot() # update title

def reset_sim(event):
    sim_state.reset()
    update_plot()

btn_play.on_clicked(toggle_play)
btn_reset.on_clicked(reset_sim)

# Slider/Text Sync Logic (Same as original)
updating_from_slider = False
def sync_text(val):
    global updating_from_slider
    updating_from_slider = True
    mode = radio.value_selected
    if mode == 'Constant Quota':
        t1.set_val(f"{int(s1.val)}")
        t2.set_val(f"{int(s2.val)}")
        t3.set_val(f"{int(s3.val)}")
    else:
        t1.set_val(f"{s1.val:.2f}")
        t2.set_val(f"{s2.val:.2f}")
        t3.set_val(f"{s3.val:.2f}")
    updating_from_slider = False

s1.on_changed(sync_text)
s2.on_changed(sync_text)
s3.on_changed(sync_text)

def submit_text(text, slider):
    if updating_from_slider: return 
    try:
        val = float(text)
        val = max(slider.valmin, min(val, slider.valmax))
        slider.set_val(val)
    except ValueError: pass 

t1.on_submit(lambda text: submit_text(text, s1))
t2.on_submit(lambda text: submit_text(text, s2))
t3.on_submit(lambda text: submit_text(text, s3))

def change_mode(label):
    # Reset sliders to 0 when mode changes to prevent instant collapse
    s1.set_val(0); s2.set_val(0); s3.set_val(0)
    
    if label == 'Constant Quota':
        limit = 800
        for s in [s1, s2, s3]: s.valmax = limit; s.ax.set_xlim(0, limit)
        s1.label.set_text("Harvest # J"); s2.label.set_text("Harvest # S"); s3.label.set_text("Harvest # A")
    elif label == 'Proportional (Uniform)':
        s1.valmax = 1.0; s1.ax.set_xlim(0, 1.0)
        s1.label.set_text("Global Rate %"); s2.label.set_text("(Inactive)"); s3.label.set_text("(Inactive)")
    elif label == 'Selective (Age-Specific)':
        for s in [s1, s2, s3]: s.valmax = 1.0; s.ax.set_xlim(0, 1.0)
        s1.label.set_text("Harvest J %"); s2.label.set_text("Harvest S %"); s3.label.set_text("Harvest A %")
    fig.canvas.draw_idle()

radio.on_clicked(change_mode)

# Animation Object
ani = FuncAnimation(fig, animate, interval=500, save_count=100) # Interval is milliseconds

# Speed Control
def update_speed(val):
    ani.event_source.interval = 1000 / val
s_speed.on_changed(update_speed)

plt.show()