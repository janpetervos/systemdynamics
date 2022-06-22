import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ipywidgets as widgets
from ipywidgets import VBox, Label, Layout
from IPython.display import display

# instellen opmaak visualisaties
sns.set(style="whitegrid", rc={"figure.figsize": (8, 4)}, font="Arial", font_scale=1.0)
kleur = ["#EC5D57", "#51A7F9", "#70BF41", "#F39019", "#F5D327", "#AA64D6"]  # rood, blauw, groen, oranje, geel, paars
sns.set_palette(kleur)

# bepalen tijdsinstellingen integratieproces
dt = 0.5 ** 3
st = 60  # [week]
n = int(st / dt)  # [week] simulatietijd
t = np.linspace(0, st, n)  # x-as voor eventuele tijdplots

# instellen exogene vraag
orders = np.ones(n) * 100
orders[int(10 / dt):] = 200


def Euler(f, x0, t, args=None):  # integrator
    n = len(t)
    x = np.array([x0] * n)
    for i in range(n - 1):
        h = t[i + 1] - t[i]
        x[i + 1] = x[i] + h * f(x[i], t[i], args)
    return x.T


def S(stocks, t, args):  # systeem

    # uitpakken parameters
    rationele_strategie, aanpassingstijd_pijplijn_eindproducten, voorspellingshorizon_eindproducten = args

    # uitpakken "stocks"
    voorraad_eindproducten, pijplijn_eindproducten, voorspelling_eindproducten = stocks

    # berekenen "flows"
    vraag = orders[int(t/dt)]
    uitstroom_eindproducten = min(voorraad_eindproducten / levertijd_eindproducten, vraag)
    instroom_eindproducten = pijplijn_eindproducten / vertraging_pijplijn_eindproducten
    vraagverandering_eindproducten = (vraag - voorspelling_eindproducten) / voorspellingshorizon_eindproducten
    voorraadaanpassing_eindproducten = (voorraadnorm_eindproducten - voorraad_eindproducten) / aanpassingstijd_voorraad_eindproducten
    gewenste_leveringen_eindproducten = voorraadaanpassing_eindproducten + voorspelling_eindproducten
    if rationele_strategie:
        gewenste_pijplijnvoorraad_eindproducten = gewenste_leveringen_eindproducten * vertraging_pijplijn_eindproducten
    else:  # eventuele voorraadverschillen worden buiten beschouwing gelaten
        gewenste_pijplijnvoorraad_eindproducten = voorspelling_eindproducten * vertraging_pijplijn_eindproducten
    aanpassing_pijplijn_eindproducten = (gewenste_pijplijnvoorraad_eindproducten - pijplijn_eindproducten) / aanpassingstijd_pijplijn_eindproducten
    bestellingen_eindproducten = max(0, aanpassing_pijplijn_eindproducten + gewenste_leveringen_eindproducten)

    return np.array([instroom_eindproducten - uitstroom_eindproducten, bestellingen_eindproducten - instroom_eindproducten, vraagverandering_eindproducten])


# instellen beginvoorwaarden voorraad, pijplijn en voorspelling
S0 = [400., 300., 100.]

# besluitvormingsstrategie
rationele_strategie = False

""" Naast de veranderingen in de doorstroom, worden ook momentane voorraadverschillen meegenomen
    in de besluitvorming. Uit simulaties blijkt dat het verschil tussen beide strategieën tamelijk
    genuanceerd is. """

# declareren constanten
levertijd_eindproducten = 1  # [week]
vertraging_pijplijn_eindproducten = 3  # [week]
voorraadnorm_eindproducten = 400  # [stuks]
aanpassingstijd_voorraad_eindproducten = 1  # [week]
voorspellingshorizon_eindproducten = 1  # [week]

# interface voor aan- of uitzetten rationele strategie
strategie_button = widgets.Checkbox(
    value=False,
    description="Rationeel",
    icon='check')

# interface voor de tijdconstante van de pijplijnvoorraad
aanpassingstijd_slider = widgets.IntSlider(
    value=1,
    min=1,
    max=10,
    step=1,
    description="[weken]",
    orientation="horizontal",
    readout_format="d")

# interface voor de tijdconstante van de voorspelling
voorspellingshorizon_slider = widgets.IntSlider(
    value=1,
    min=1,
    max=10,
    step=1,
    description="[weken]",
    orientation="horizontal",
    readout_format="d")

# instellen user interface
label_layout = Layout(width='600px',height='30px')
tab1 = VBox([Label("Aanpassingstijd mutaties pijplijnvoorraad gehanteerd door het management",layout=label_layout), aanpassingstijd_slider])
tab2 = VBox([Label("Strategie voor pijplijnvoorraad gehanteerd door het management",layout=label_layout), strategie_button])
tab3 = VBox([Label("Voorspellingshorizon gehanteerd door het management",layout=label_layout), voorspellingshorizon_slider])
tab = widgets.Tab(children=[tab1, tab2, tab3])
tab.set_title(0, "Pijplijnvoorraad")
tab.set_title(1, "Strategie")
tab.set_title(2, "Voorspellingshorizon")
display(tab)

# uitvoeren simulatie en visualiseren resultaten
@widgets.interact_manual()
def plot():
    strategie = strategie_button.value
    aanpassingstijd = aanpassingstijd_slider.value
    voorspellingshorizon = voorspellingshorizon_slider.value
    parameters = (strategie, aanpassingstijd, voorspellingshorizon)
    stocks = Euler(S, S0, t, args=parameters)
    voorraad_eindproducten, pijplijn_eindproducten, voorspelling_eindproducten = stocks
    totale_voorraad = voorraad_eindproducten + pijplijn_eindproducten

    # %% visualiseren voorraadniveaus
    fig1, ax = plt.subplots(2, 1, figsize=(8, 8), sharex="all")
    ax[0].plot(t, voorraad_eindproducten, label="Voorraad")
    ax[0].plot(t, pijplijn_eindproducten, color=kleur[1], label="Pijplijn")
    ax[1].plot(t, totale_voorraad, color=kleur[3], label="Totale voorraad")
    ax[0].set_title("Tijdsverloop eindvoorraad en pijplijnvoorraad", fontweight="bold")
    ax[1].set_title("Tijdsverloop totale voorraad in de distributieketen", fontweight="bold")
    ax[1].set_xlabel("Tijd [week]")
    ax[0].set_ylabel("Voorraad [stuks]")
    ax[1].set_ylabel("Voorraad [stuks]")
    ax[0].legend()
    ax[1].legend()
    plt.tight_layout()
    plt.show()

    # %% visualiseren vraagvoorspelling
    fig2 = plt.figure(figsize=(7.3, 4))
    plt.plot(t, orders, label="Vraag")
    plt.plot(t, voorspelling_eindproducten, label="Voorspelling")
    plt.title("Tijdsverloop vraag en vraagvoorspelling", fontname="Avenir Next")
    plt.xlabel("Tijd [week]")
    plt.ylabel("Vraag [stuks]")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.show()

    # %% visualiseren fasediagram
    fig3 = plt.figure(figsize=(4, 4))
    plt.plot(voorraad_eindproducten, pijplijn_eindproducten, color=kleur[2])
    plt.title("Fasediagram voorraad en pijplijn", fontweight="bold")
    plt.xlabel("Voorraad [stuks]")
    plt.ylabel("Pijplijn [stuks]")
    plt.tight_layout()
    plt.show()
