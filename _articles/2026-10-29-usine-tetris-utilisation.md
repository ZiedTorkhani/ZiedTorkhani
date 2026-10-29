---
titre: Votre usine joue à Tetris : pourquoi une usine pleine est toujours en retard
description: Plus une machine approche 100 % de charge, plus les délais explosent. La loi de Factory Physics derrière ce constat, et ce qu'elle change pour planifier.
date: 2026-10-29
---

Lundi matin, le plan de la semaine est parfait. Chargé à 100 %. Tout s'emboîte.

Mardi, 10 h : un gros client appelle. C'est urgent.

À partir de là, l'usine devient une partie de Tetris.

## Ce qui se passe dans le plan

1. **La pièce urgente ne rentre nulle part.** On déplace d'autres commandes pour lui faire de la place.
2. **Des trous apparaissent.** Changements de série imprévus, attente de matière, réglages : du temps perdu qui ne revient pas.
3. **Des blocs dépassent en haut.** Ce sont des commandes qui ne seront pas livrées à temps.

On connaît la suite. Le planificateur passe sa semaine à replanifier, les promesses aux clients glissent, et tout le monde a l'impression que le plan « ne tient jamais ».

## Ce n'est pas le planificateur, c'est une loi

Wallace Hopp et Mark Spearman l'expliquent dans *Factory Physics* : quand une ressource approche 100 % d'utilisation, le temps d'attente devant elle n'augmente pas un peu. Il explose.

À variabilité égale, et en prenant une machine chargée à 50 % comme point de comparaison, la forme la plus simple de cette loi donne :

<figure class="chart">
<svg viewBox="0 0 640 340" role="img" aria-labelledby="fig-titre fig-desc">
<title id="fig-titre">Temps d'attente selon le taux d'utilisation d'une machine</title>
<desc id="fig-desc">La courbe reste presque plate de 50 % à 80 % d'utilisation, puis monte très vite : le temps d'attente est multiplié par 4 à 80 %, par 9 à 90 % et par 19 à 95 %, comparé à une machine chargée à 50 %.</desc>
<g class="grid"><line x1="64" y1="238.4" x2="604" y2="238.4"/><line x1="64" y1="184.8" x2="604" y2="184.8"/><line x1="64" y1="131.2" x2="604" y2="131.2"/><line x1="64" y1="77.6" x2="604" y2="77.6"/></g>
<line class="axis" x1="64" y1="292" x2="604" y2="292"/>
<g class="tick"><text x="56" y="296" text-anchor="end">0</text><text x="56" y="242.4" text-anchor="end">×5</text><text x="56" y="188.8" text-anchor="end">×10</text><text x="56" y="135.2" text-anchor="end">×15</text><text x="56" y="81.6" text-anchor="end">×20</text></g>
<g class="tick"><text x="64" y="316" text-anchor="middle">50 %</text><text x="181.4" y="316" text-anchor="middle">60 %</text><text x="298.8" y="316" text-anchor="middle">70 %</text><text x="416.2" y="316" text-anchor="middle">80 %</text><text x="533.6" y="316" text-anchor="middle">90 %</text></g>
<text class="axis-title" x="604" y="336" text-anchor="end">Taux d'utilisation de la machine</text>
<path class="curve" d="M64.0,281.3 L75.7,280.8 L87.5,280.4 L99.2,279.9 L111.0,279.4 L122.7,278.9 L134.4,278.4 L146.2,277.8 L157.9,277.2 L169.7,276.6 L181.4,275.9 L193.1,275.2 L204.9,274.5 L216.6,273.7 L228.3,272.9 L240.1,272.1 L251.8,271.2 L263.6,270.2 L275.3,269.2 L287.0,268.1 L298.8,267.0 L310.5,265.8 L322.3,264.4 L334.0,263.0 L345.7,261.5 L357.5,259.8 L369.2,258.1 L381.0,256.1 L392.7,254.0 L404.4,251.7 L416.2,249.1 L427.9,246.3 L439.7,243.2 L451.4,239.7 L463.1,235.7 L474.9,231.3 L486.6,226.1 L498.3,220.3 L510.1,213.4 L521.8,205.3 L533.6,195.5 L545.3,183.6 L557.0,168.7 L568.8,149.6 L580.5,124.1 L586.4,107.8 L592.3,88.3 L598.1,64.5 L604.0,34.7"/>
<g class="point"><circle cx="64" cy="281.3" r="4.5"/><circle cx="416.2" cy="249.1" r="4.5"/><circle cx="533.6" cy="195.5" r="4.5"/><circle cx="592.3" cy="88.3" r="4.5"/></g>
<g class="label"><text x="72" y="270">×1</text><text x="416.2" y="236" text-anchor="middle">×4</text><text x="522" y="190" text-anchor="end">×9</text><text x="580" y="86" text-anchor="end">×19 à 95 %</text></g>
</svg>
<figcaption>Temps d'attente devant une machine, comparé à une machine chargée à 50 %. Forme simplifiée u / (1 − u), à variabilité égale : un ordre de grandeur, pas une prévision.</figcaption>
</figure>

<table class="data">
<caption>Les mêmes valeurs en tableau</caption>
<thead><tr><th scope="col">Utilisation</th><th scope="col">Temps d'attente comparé à 50 %</th></tr></thead>
<tbody><tr><td>50 %</td><td>× 1</td></tr><tr><td>80 %</td><td>× 4</td></tr><tr><td>90 %</td><td>× 9</td></tr><tr><td>95 %</td><td>× 19</td></tr></tbody>
</table>

La courbe reste plate longtemps, puis elle monte d'un coup. C'est pour ça qu'une usine « pleine » est presque toujours en retard : elle vit dans la partie droite de la courbe, là où la moindre urgence se transforme en semaines d'attente.

## D'où vient la courbe

Le livre donne une approximation (la formule de Kingman) qui tient en trois facteurs multipliés entre eux :

> Temps d'attente ≈ variabilité × utilisation × temps de traitement

- **La variabilité** : à quel point les arrivées de commandes et les temps de production s'écartent de la moyenne. Une demande qui arrive par vagues et des réglages imprévisibles la font grimper.
- **L'utilisation** : le facteur u / (1 − u) de la courbe ci-dessus. C'est lui qui explose près de 100 %.
- **Le temps de traitement** : la durée moyenne d'une opération sur la machine.

Les trois se multiplient. Une machine très chargée mais très régulière peut tenir. Une machine très chargée et très variable ne tiendra pas, peu importe le talent du planificateur.

## Ce que ça change pour planifier

**Arrêter de viser 100 %.** Un plan chargé à 100 % n'est pas efficace : il est fragile. La capacité qu'on garde libre, c'est l'assurance contre l'imprévu.

**Garder la marge là où elle compte.** Inutile de la garder partout. Elle sert surtout sur le goulot et sur les ressources où arrivent les urgences.

**Réduire la variabilité, l'autre levier.** Si on ne peut pas baisser la charge, on peut réduire les écarts : des changements de série plus courts, une matière qui arrive à l'heure, des commandes lissées plutôt que groupées. Chaque point de variabilité en moins fait reculer la courbe.

**Choisir son tampon.** *Factory Physics* le résume bien : la variabilité finit toujours par se payer, en stock, en capacité ou en délai. Si on ne choisit pas lequel, c'est le délai qui paie, et c'est le client qui le voit.

## En une phrase

Une usine planifiée à 100 % n'a plus de place pour l'imprévu, et l'imprévu arrive toujours : gardez de la marge sur le goulot, ou réduisez la variabilité, sinon c'est le client qui attendra.

*Source : Wallace J. Hopp et Mark L. Spearman, Factory Physics. Les valeurs du graphique sont calculées avec la forme simplifiée u / (1 − u) ; la valeur réelle dépend de la variabilité de chaque atelier.*
