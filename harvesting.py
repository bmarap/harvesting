import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons, TextBox

# --- 1. CONFIGURATION ---
INITIAL_POP = np.array([1000.0, 500.0, 200.0]) # Biological Parameters
F_J, F_S, F_A = 0.0, 0.8, 2.5 
S_J_to_S = 0.5 
S_S_to_A = 0.7
S_A_surv = 0.8  

YEARS = 50

# --- 2. SIMULATION ENGINE ---
def run_simulation(val_j, val_s, val_a, mode):
    history = np.zeros((YEARS + 1, 3))
    history[0] = INITIAL_POP
    current_pop = INITIAL_POP.copy()
    
    for t in range(YEARS):
        survivors = np.zeros(3)
        
        if mode == 'Constant Quota':
            survivors[0] = max(0, current_pop[0] - val_j)
            survivors[1] = max(0, current_pop[1] - val_s)
            survivors[2] = max(0, current_pop[2] - val_a)
            
        elif mode == 'Proportional (Uniform)':
            global_rate = val_j 
            survivors = current_pop * (1 - global_rate)
            
        elif mode == 'Selective (Age-Specific)':
            survivors[0] = current_pop[0] * (1 - val_j)
            survivors[1] = current_pop[1] * (1 - val_s)
            survivors[2] = current_pop[2] * (1 - val_a)

        next_j = (survivors[0] * F_J) + (survivors[1] * F_S) + (survivors[2] * F_A)
        next_s = survivors[0] * S_J_to_S
        next_a = (survivors[1] * S_S_to_A) + (survivors[2] * S_A_surv)
        
        current_pop = np.array([next_j, next_s, next_a])
        history[t+1] = current_pop
        
    return history

# --- 3. PLOTTING SETUP ---
fig, ax = plt.subplots(figsize=(14, 7))

plt.subplots_adjust(left=0.1, bottom=0.35, right=0.70) 

initial_data = run_simulation(0, 0, 0, 'Selective (Age-Specific)')
t_range = np.arange(YEARS + 1)

l_j, = ax.plot(t_range, initial_data[:, 0], lw=2, label='Juvenile')
l_s, = ax.plot(t_range, initial_data[:, 1], lw=2, label='Sub-Adult')
l_a, = ax.plot(t_range, initial_data[:, 2], lw=2, label='Adult')
l_tot, = ax.plot(t_range, np.sum(initial_data, axis=1), 'k--', lw=2, label='Total')

ax.set_title("Harvesting Strategy Simulation")
ax.set_xlabel("Time (Years)")
ax.set_ylabel("Population Size")
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_ylim(0, np.max(initial_data)*1.2)

param_text = (
    "BIOLOGICAL PARAMETERS\n"
    "---------------------\n"
    f"Initial Pop:\n"
    f"  J: {INITIAL_POP[0]}\n"
    f"  S: {INITIAL_POP[1]}\n"
    f"  A: {INITIAL_POP[2]}\n\n"
    f"Fecundity (F):\n"
    f"  J: {F_J}\n"
    f"  S: {F_S}\n"
    f"  A: {F_A}\n\n"
    f"Survival Rates (S):\n"
    f"  J -> S: {S_J_to_S}\n"
    f"  S -> A: {S_S_to_A}\n"
    f"  A -> A: {S_A_surv}"
)

fig.text(0.72, 0.60, param_text, fontsize=10, family='monospace', 
         verticalalignment='center', bbox=dict(boxstyle='round', facecolor='whitesmoke', alpha=0.8))


# --- 4. CONTROLS ---
axcolor = 'lightgoldenrodyellow'

# Geometry
slider_width = 0.35
text_width = 0.08
x_slider = 0.15
x_text = 0.55

# Axes
ax_s1 = plt.axes([x_slider, 0.20, slider_width, 0.03], facecolor=axcolor)
ax_s2 = plt.axes([x_slider, 0.15, slider_width, 0.03], facecolor=axcolor)
ax_s3 = plt.axes([x_slider, 0.10, slider_width, 0.03], facecolor=axcolor)

ax_t1 = plt.axes([x_text, 0.20, text_width, 0.03])
ax_t2 = plt.axes([x_text, 0.15, text_width, 0.03])
ax_t3 = plt.axes([x_text, 0.10, text_width, 0.03])

s1 = Slider(ax_s1, 'Harvest J', 0.0, 1.0, valinit=0.0)
s2 = Slider(ax_s2, 'Harvest S', 0.0, 1.0, valinit=0.0)
s3 = Slider(ax_s3, 'Harvest A', 0.0, 1.0, valinit=0.0)

s1.valtext.set_visible(False)
s2.valtext.set_visible(False)
s3.valtext.set_visible(False)

t1 = TextBox(ax_t1, '', initial='0.00')
t2 = TextBox(ax_t2, '', initial='0.00')
t3 = TextBox(ax_t3, '', initial='0.00')

ax_radio = plt.axes([0.72, 0.10, 0.18, 0.15], facecolor=axcolor)
radio = RadioButtons(ax_radio, ('Constant Quota', 'Proportional (Uniform)', 'Selective (Age-Specific)'), active=2)

# --- 5. LOGIC ---
updating_from_slider = False

def update_simulation(val=None):
    global updating_from_slider
    updating_from_slider = True
    
    mode = radio.value_selected
    data = run_simulation(s1.val, s2.val, s3.val, mode)
    
    l_j.set_ydata(data[:, 0])
    l_s.set_ydata(data[:, 1])
    l_a.set_ydata(data[:, 2])
    l_tot.set_ydata(np.sum(data, axis=1))
    
    current_max = np.max(data)
    if current_max < 10: current_max = 10
    ax.set_ylim(0, current_max * 1.1)
    
    if mode == 'Constant Quota':
        t1.set_val(f"{int(s1.val)}")
        t2.set_val(f"{int(s2.val)}")
        t3.set_val(f"{int(s3.val)}")
    else:
        t1.set_val(f"{s1.val:.2f}")
        t2.set_val(f"{s2.val:.2f}")
        t3.set_val(f"{s3.val:.2f}")

    updating_from_slider = False
    fig.canvas.draw_idle()

def submit_text(text, slider):
    if updating_from_slider: return 
    try:
        val = float(text)
        if val < slider.valmin: val = slider.valmin
        if val > slider.valmax: val = slider.valmax
        slider.set_val(val)
    except ValueError:
        pass 

t1.on_submit(lambda text: submit_text(text, s1))
t2.on_submit(lambda text: submit_text(text, s2))
t3.on_submit(lambda text: submit_text(text, s3))

s1.on_changed(update_simulation)
s2.on_changed(update_simulation)
s3.on_changed(update_simulation)

def change_mode(label):
    s1.set_val(0)
    s2.set_val(0)
    s3.set_val(0)

    if label == 'Constant Quota':
        limit = 800
        s1.valmax = limit; s1.ax.set_xlim(0, limit)
        s2.valmax = limit; s2.ax.set_xlim(0, limit)
        s3.valmax = limit; s3.ax.set_xlim(0, limit)
        s1.label.set_text("Harvest # J")
        s2.label.set_text("Harvest # S")
        s3.label.set_text("Harvest # A")
        
    elif label == 'Proportional (Uniform)':
        s1.valmax = 1.0; s1.ax.set_xlim(0, 1.0)
        s1.label.set_text("Global Rate %")
        s2.label.set_text("(Inactive)")
        s3.label.set_text("(Inactive)")
        
    elif label == 'Selective (Age-Specific)':
        s1.valmax = 1.0; s1.ax.set_xlim(0, 1.0)
        s2.valmax = 1.0; s2.ax.set_xlim(0, 1.0)
        s3.valmax = 1.0; s3.ax.set_xlim(0, 1.0)
        s1.label.set_text("Harvest J %")
        s2.label.set_text("Harvest S %")
        s3.label.set_text("Harvest A %")

    update_simulation()

radio.on_clicked(change_mode)

plt.show()