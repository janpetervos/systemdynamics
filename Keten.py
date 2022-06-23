import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ipywidgets as widgets
from ipywidgets import VBox, Label, Layout
from IPython.display import display

# instellen opmaak visualisaties
# sns.set(style="whitegrid", rc={"figure.figsize": (8, 4)}, font="Arial", font_scale=1.0)
sns.set(style="whitegrid", rc={"figure.figsize": (8, 4)}, font_scale=1.0)
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
    rationele_strategie, aanpassingstijd_pijplijn_eindproducten, aanpassingstijd_pijplijn_componenten, aanpassingstijd_pijplijn_onderdelen, voorspellingshorizon_eindproducten, voorspellingshorizon_componenten, voorspellingshorizon_onderdelen = args

    # uitpakken "stocks"
    voorraad_eindproducten, pijplijn_eindproducten, voorspelling_eindproducten, voorraad_componenten, pijplijn_componenten, voorspelling_componenten, voorraad_onderdelen, pijplijn_onderdelen, voorspelling_onderdelen = stocks

    # berekenen "flows" Eindproducten
    vraag = orders[int(t/dt)]
    uitstroom_eindproducten = min(voorraad_eindproducten / levertijd_eindproducten, vraag)
    instroom_eindproducten = pijplijn_eindproducten / vertraging_pijplijn_eindproducten
    vraagverandering_eindproducten = (vraag - voorspelling_eindproducten) / voorspellingshorizon_eindproducten
    voorraadaanpassing_eindproducten = \
        (voorraadnorm_eindproducten - voorraad_eindproducten) / aanpassingstijd_voorraad_eindproducten
    gewenste_leveringen_eindproducten = voorraadaanpassing_eindproducten + voorspelling_eindproducten
    if rationele_strategie:
        gewenste_pijplijnvoorraad_eindproducten = gewenste_leveringen_eindproducten * vertraging_pijplijn_eindproducten
    else:  # eventuele voorraadverschillen worden buiten beschouwing gelaten
        gewenste_pijplijnvoorraad_eindproducten = voorspelling_eindproducten * vertraging_pijplijn_eindproducten
    aanpassing_pijplijn_eindproducten = \
        (gewenste_pijplijnvoorraad_eindproducten - pijplijn_eindproducten) / aanpassingstijd_pijplijn_eindproducten
    bestellingen_eindproducten = max(0, aanpassing_pijplijn_eindproducten + gewenste_leveringen_eindproducten)

    # berekenen "flows" Componenten
    uitstroom_componenten = min(bestellingen_eindproducten, voorraad_componenten / levertijd_componenten)
    instroom_componenten = pijplijn_componenten / vertraging_pijplijn_componenten
    vraagverandering_componenten = \
        (uitstroom_componenten - voorspelling_componenten) / voorspellingshorizon_componenten
    voorraadaanpassing_componenten = \
        (voorraadnorm_componenten - voorraad_componenten) / aanpassingstijd_voorraad_componenten
    gewenste_leveringen_componenten = voorraadaanpassing_componenten + voorspelling_componenten
    if rationele_strategie:
        gewenste_pijplijnvoorraad_componenten = gewenste_leveringen_componenten * vertraging_pijplijn_componenten
    else:  # eventuele voorraadverschillen worden buiten beschouwing gelaten
        gewenste_pijplijnvoorraad_componenten = voorspelling_componenten * vertraging_pijplijn_componenten
    aanpassing_pijplijn_componenten = \
        (gewenste_pijplijnvoorraad_componenten - pijplijn_componenten) / aanpassingstijd_pijplijn_componenten
    bestellingen_componenten = max(0, aanpassing_pijplijn_componenten + gewenste_leveringen_componenten)

    # berekenen "flows" Onderdelen
    uitstroom_onderdelen = min(bestellingen_componenten, voorraad_onderdelen / levertijd_onderdelen)
    instroom_onderdelen = pijplijn_onderdelen / vertraging_pijplijn_onderdelen
    vraagverandering_onderdelen = (uitstroom_onderdelen - voorspelling_onderdelen) / voorspellingshorizon_onderdelen
    voorraadaanpassing_onderdelen =\
        (voorraadnorm_onderdelen - voorraad_onderdelen) / aanpassingstijd_voorraad_onderdelen
    gewenste_leveringen_onderdelen = voorraadaanpassing_onderdelen + voorspelling_onderdelen
    if rationele_strategie:
        gewenste_pijplijnvoorraad_onderdelen = gewenste_leveringen_onderdelen * vertraging_pijplijn_onderdelen
    else:  # eventuele voorraadverschillen worden buiten beschouwing gelaten
        gewenste_pijplijnvoorraad_onderdelen = voorspelling_onderdelen * vertraging_pijplijn_onderdelen
    aanpassing_pijplijn_onderdelen = \
        (gewenste_pijplijnvoorraad_onderdelen - pijplijn_onderdelen) / aanpassingstijd_pijplijn_onderdelen
    bestellingen_onderdelen = max(0, aanpassing_pijplijn_onderdelen + gewenste_leveringen_onderdelen)
    instroom_grondstoffen = bestellingen_onderdelen

    return np.array([instroom_eindproducten - uitstroom_eindproducten,
                     uitstroom_componenten - instroom_eindproducten,
                     vraagverandering_eindproducten,
                     instroom_componenten - uitstroom_componenten,
                     uitstroom_onderdelen - instroom_componenten,
                     vraagverandering_componenten,
                     instroom_onderdelen - uitstroom_onderdelen,
                     instroom_grondstoffen - instroom_onderdelen,
                     vraagverandering_onderdelen])

# instellen beginvoorwaarden voorraad, pijplijn en voorspelling
S0 = [400., 300., 100., 400., 300., 100., 400., 300., 100.]

# besluitvormingsstrategie
rationele_strategie = False

""" Naast de veranderingen in de doorstroom, worden ook momentane voorraadverschillen meegenomen
    in de besluitvorming. Uit simulaties blijkt dat het verschil tussen beide strategieën tamelijk
    genuanceerd is. """

# declareren constanten
levertijd_eindproducten = 1  # [week]
levertijd_componenten = 1  # [week]
levertijd_onderdelen = 1  # [week]
vertraging_pijplijn_eindproducten = 3  # [week]
vertraging_pijplijn_componenten = 3  # [week]
vertraging_pijplijn_onderdelen = 3  # [week]
voorraadnorm_eindproducten = 400  # [stuks]
voorraadnorm_componenten = 400  # [stuks]
voorraadnorm_onderdelen = 400  # [stuks]
aanpassingstijd_voorraad_eindproducten = 1  # [week]
aanpassingstijd_voorraad_componenten = 1  # [week]
aanpassingstijd_voorraad_onderdelen = 1  # [week]

# interface voor aan- of uitzetten rationele strategie
strategie_button = widgets.Checkbox(
    value=False,
    description="Rationeel",
    icon='check')

# interface voor de tijdconstante van de pijplijnvoorraad
style = {'description_width': 'initial'}
aanpassingstijd_pijplijn_eindproducten_slider = widgets.IntSlider(
    value=10,
    min=1,
    max=10,
    step=1,
    description="Eindproducten [week]",
    style=style,
    readout_format="d")
aanpassingstijd_pijplijn_componenten_slider = widgets.IntSlider(
    value=10,
    min=1,
    max=10,
    step=1,
    description="Componenten [week]",
    style=style,
    readout_format="d")
aanpassingstijd_pijplijn_onderdelen_slider = widgets.IntSlider(
    value=10,
    min=1,
    max=10,
    step=1,
    description="Onderdelen [week]",
    style=style,
    readout_format="d")

# interface voor de tijdconstante van de voorspelling
voorspellingshorizon_eindproducten_slider = widgets.IntSlider(
    value=1,
    min=1,
    max=10,
    step=1,
    description="Eindproducten [week]",
    style=style,
    readout_format="d")
voorspellingshorizon_componenten_slider = widgets.IntSlider(
    value=1,
    min=1,
    max=10,
    step=1,
    description="Componenten [week]",
    style=style,
    readout_format="d")
voorspellingshorizon_onderdelen_slider = widgets.IntSlider(
    value=1,
    min=1,
    max=10,
    step=1,
    description="Onderdelen [week]",
    style=style,
    readout_format="d")

# instellen user interface
label_layout = Layout(width='600px',height='30px')
tab1 = VBox(children=[aanpassingstijd_pijplijn_eindproducten_slider,
                      aanpassingstijd_pijplijn_componenten_slider,
                      aanpassingstijd_pijplijn_onderdelen_slider])
tab2 = VBox([Label("Strategie voor pijplijnvoorraad gehanteerd door het management",layout=label_layout), strategie_button])
tab3 = VBox(children=[voorspellingshorizon_eindproducten_slider,
                      voorspellingshorizon_componenten_slider,
                      voorspellingshorizon_onderdelen_slider])
tab = widgets.Tab(children=[tab1, tab2, tab3])
tab.set_title(0, "Pijplijnvoorraad")
tab.set_title(1, "Strategie")
tab.set_title(2, "Voorspellingshorizon")
display(tab)

# uitvoeren simulatie en visualiseren resultaten
@widgets.interact_manual()
def plot():
    strategie = strategie_button.value
    aanpassingstijd_pijplijn_eindproducten = aanpassingstijd_pijplijn_eindproducten_slider.value
    aanpassingstijd_pijplijn_componenten = aanpassingstijd_pijplijn_componenten_slider.value
    aanpassingstijd_pijplijn_onderdelen = aanpassingstijd_pijplijn_onderdelen_slider.value
    voorspellingshorizon_eindproducten = voorspellingshorizon_eindproducten_slider.value
    voorspellingshorizon_componenten = voorspellingshorizon_componenten_slider.value
    voorspellingshorizon_onderdelen = voorspellingshorizon_onderdelen_slider.value
    parameters = (strategie, aanpassingstijd_pijplijn_eindproducten, aanpassingstijd_pijplijn_componenten, aanpassingstijd_pijplijn_onderdelen, voorspellingshorizon_eindproducten, voorspellingshorizon_componenten, voorspellingshorizon_onderdelen)
    stocks = Euler(S, S0, t, args=parameters)
    voorraad_eindproducten, pijplijn_eindproducten, voorspelling_eindproducten, voorraad_componenten, pijplijn_componenten, voorspelling_componenten, voorraad_onderdelen, pijplijn_onderdelen, voorspelling_onderdelen = stocks
    totale_voorraad = voorraad_eindproducten + pijplijn_eindproducten + voorraad_componenten + pijplijn_componenten + voorraad_onderdelen + pijplijn_onderdelen

    # %% visualiseren eindvoorraad en pijplijnvoorraad per schakel in de distributieketen
    fig1, ax = plt.subplots(3, 1, sharex="all", figsize=(8, 12))
    ax[0].plot(t, voorraad_eindproducten, label="Voorraad")
    ax[0].plot(t, pijplijn_eindproducten, label="Pijplijn")
    ax[1].plot(t, voorraad_componenten, label="Voorraad")
    ax[1].plot(t, pijplijn_componenten, label="Pijplijn")
    ax[2].plot(t, voorraad_onderdelen, label="Voorraad")
    ax[2].plot(t, pijplijn_onderdelen, label="Pijplijn")
    ax[0].set_title("Eindproducten", fontweight="bold")
    ax[1].set_title("Componenten", fontweight="bold")
    ax[2].set_title("Onderdelen", fontweight="bold")
    ax[2].set_xlabel("Tijd [week]")
    for axi in ax.flat:
        axi.legend(loc="upper left")
        axi.set_ylabel("Voorraad [stuks]")
        axi.set_ylim([0, 1400])
    plt.tight_layout()
    plt.show()

    # %% visualiseren voorraadniveaus
    fig2, ax = plt.subplots(3, 1, figsize=(8, 12), sharex="all")
    ax[0].plot(t, voorraad_eindproducten, label="Eindproducten")
    ax[0].plot(t, voorraad_componenten, label="Componenten")
    ax[0].plot(t, voorraad_onderdelen, label="Onderdelen")
    ax[1].plot(t, pijplijn_eindproducten, label="Eindproducten")
    ax[1].plot(t, pijplijn_componenten, label="Componenten")
    ax[1].plot(t, pijplijn_onderdelen, label="Onderdelen")
    ax[2].plot(t, totale_voorraad, color=kleur[3], label="Totale voorraad")
    ax[0].set_title("Tijdsverloop eindvoorraden in de distributieketen", fontweight="bold")
    ax[1].set_title("Tijdsverloop pijplijnvoorraden in de distributieketen", fontweight="bold")
    ax[2].set_title("Tijdsverloop totale voorraad in de distributieketen", fontweight="bold")
    ax[2].set_xlabel("Tijd [week]")
    for axi in ax.flat:
        axi.set_ylabel("Voorraad [stuks]")
        axi.legend(loc="best")
    plt.tight_layout()
    plt.show()

    # %% visualiseren eindvraag en voorspellingen
    fig3 = plt.figure(figsize=(8, 4))
    plt.plot(t, orders, label="Vraag")
    plt.plot(t, voorspelling_eindproducten, label="Eindproducten")
    plt.plot(t, voorspelling_componenten, label="Componenten")
    plt.plot(t, voorspelling_onderdelen, label="Onderdelen")
    plt.title("Tijdsverloop vraag en vraagvoorspelling", fontweight="bold")
    plt.xlabel("Tijd [week]")
    plt.ylabel("Vraag [stuks]")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.show()

    # %% visualiseren fasediagrammen van eindvoorraad en pijplijnvoorraad per schakel in de distributieketen
    fig4, ax = plt.subplots(1, 3, figsize=(12, 4))
    ax[0].plot(voorraad_eindproducten, pijplijn_eindproducten, color=kleur[0])
    ax[1].plot(voorraad_componenten, pijplijn_componenten, color=kleur[1])
    ax[2].plot(voorraad_onderdelen, pijplijn_onderdelen, color=kleur[2])
    ax[0].set_title("Fasediagram Eindproducten", fontweight="bold")
    ax[0].set_xlabel("Voorraad [stuks]")
    ax[0].set_ylabel("Pijplijn [stuks]")
    ax[1].set_title("Fasediagram Componenten", fontweight="bold")
    ax[1].set_xlabel("Voorraad [stuks]")
    ax[1].set_ylabel("Pijplijn [stuks]")
    ax[2].set_title("Fasediagram Onderdelen", fontweight="bold")
    ax[2].set_xlabel("Voorraad [stuks]")
    ax[2].set_ylabel("Pijplijn [stuks]")
    plt.tight_layout()
    plt.show()
