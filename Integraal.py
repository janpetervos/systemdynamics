import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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
vraag = np.ones(n) * 100
vraag[int(10 / dt):] = 200

# declareren toestandsvariabelen
backlog = np.zeros(n)  # [stuks]
voorraad_eindproducten = np.zeros(n)  # [stuks]
voorraad_componenten = np.zeros(n)  # [stuks]
voorraad_onderdelen = np.zeros(n)  # [stuks]

# declareren constanten
levertijd_eindproducten = 3  # [week]
levertijd_componenten = 3  # [week]
levertijd_onderdelen = 3  # [week]
levertijd_grondstoffen = 3  # [week]

# instellen beginvoorwaarden
backlog[0] = 1200  # [stuks]
voorraad_eindproducten[0] = 300  # [stuks]
voorraad_componenten[0] = 300  # [stuks]
voorraad_onderdelen[0] = 300  # [stuks]

# uitvoeren simulatie
for i in range(n):  # Euler-integratie

    # berekenen "flows" voorraad eindproducten
    levering_eindproducten = min(voorraad_eindproducten[i], backlog[i]) / levertijd_eindproducten

    # berekenen "flows" backlog
    orders_klanten = vraag[i]
    verwerkte_orders = levering_eindproducten

    # berekenen "flows" voorraad componenten
    levering_componenten = voorraad_componenten[i] / levertijd_componenten

    # berekenen "flows" voorraad onderdelen
    levering_onderdelen = voorraad_onderdelen[i] / levertijd_onderdelen
    voorraadverschil = backlog[i] - voorraad_eindproducten[i] - voorraad_componenten[i] - voorraad_onderdelen[i]
    levering_grondstoffen = max(0, voorraadverschil / levertijd_grondstoffen)

    # berekenen "stocks"
    if i < n - 1:
        # volgende toestanden
        backlog[i + 1] = backlog[i] + (orders_klanten - verwerkte_orders) * dt
        voorraad_eindproducten[i + 1] = voorraad_eindproducten[i] + (levering_componenten - levering_eindproducten) * dt
        voorraad_componenten[i + 1] = voorraad_componenten[i] + (levering_onderdelen - levering_componenten) * dt
        voorraad_onderdelen[i + 1] = voorraad_onderdelen[i] + (levering_grondstoffen - levering_onderdelen) * dt

totale_voorraad = voorraad_eindproducten + voorraad_componenten + voorraad_onderdelen

# %% visualiseren backlog
fig1, ax = plt.subplots()
plt.title("Tijdsverloop backlog", fontweight="bold")
plt.plot(t, backlog, label="Backlog")
ax.annotate("1e-orde exp. vertraging",
            xy=(21, 2090), xycoords='data',
            xytext=(0.6, 0.575), textcoords='figure fraction',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc", color="0.4"),)
plt.xlabel("Tijd [week]")
plt.ylabel("Voorraad [stuks]")
plt.legend(loc="best")
plt.tight_layout()
plt.show()

# %% visualiseren voorraden
fig2, ax = plt.subplots()
plt.title("Tijdsverloop eindvoorraden in de distributieketen", fontweight="bold")
plt.plot(t, voorraad_eindproducten, label="Eindproducten")
plt.plot(t, voorraad_componenten, label="Componenten")
plt.plot(t, voorraad_onderdelen, label="Onderdelen")
ax.annotate("4e-orde exp. vertraging",
            xy=(20, 430), xycoords='data',
            xytext=(0.6, 0.46), textcoords='figure fraction',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc", color="0.4"),)
ax.annotate("3e-orde exp. vertraging",
            xy=(19.5, 485), xycoords='data',
            xytext=(0.6, 0.58), textcoords='figure fraction',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc", color="0.4"),)
ax.annotate("2e-orde exp. vertraging",
            xy=(18.9, 540), xycoords='data',
            xytext=(0.6, 0.70), textcoords='figure fraction',
            arrowprops=dict(arrowstyle="->", connectionstyle="arc", color="0.4"),)
plt.xlabel("Tijd [week]")
plt.ylabel("Voorraad [stuks]")
plt.legend(loc="best")
plt.tight_layout()
plt.show()

# %% visualiseren totale voorraad
fig3 = plt.figure()
plt.title("Tijdsverloop totale voorraad in de distributieketen", fontweight="bold")
plt.plot(t, totale_voorraad, color=kleur[3], label="Totale voorraad")
plt.xlabel("Tijd [week]")
plt.ylabel("Voorraad [stuks]")
plt.legend(loc="best")
plt.tight_layout()
plt.show()

# %% visualiseren fasediagrammen van schakels in de distributieketen
fig4, ax = plt.subplots(1, 3, figsize=(12, 4))
ax[0].plot(voorraad_eindproducten, voorraad_componenten, color=kleur[0])
ax[1].plot(voorraad_eindproducten, voorraad_onderdelen, color=kleur[1])
ax[2].plot(voorraad_componenten, voorraad_onderdelen, color=kleur[2])
ax[0].set_xlabel("Eindproducten [stuks]")
ax[0].set_ylabel("Componenten [stuks]")
ax[1].set_xlabel("Eindproducten [stuks]")
ax[1].set_ylabel("Onderdelen [stuks]")
ax[2].set_xlabel("Componenten [stuks]")
ax[2].set_ylabel("Onderdelen [stuks]")
plt.tight_layout()
plt.show()
