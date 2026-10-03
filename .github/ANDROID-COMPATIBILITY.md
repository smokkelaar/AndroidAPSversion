# Releases voor de verschillende Android-versies

Gecontroleerd op **3 oktober 2026** tegen de officiële
[AAPS-release notes](https://wiki.aaps.app/en/latest/Maintenance/ReleaseNotes.html#android-version-and-aaps-version)
en de bijbehorende upstream-broncode.

| Android op de telefoon | Laatste aangewezen AAPS-versie | Bron voor deze selectie |
| --- | --- | --- |
| 12 en nieuwer | **3.4.2.6** | Tag `3.4.2.6`; huidige `master` |
| 11 | **3.3.2.1** | Branch `v3.3.2.1` |
| 9 en 10 | **3.2.0.4** | Branch `v3.2.0.4` |
| 8.0 en 8.1 | **2.8.2.1** | Branch `v2.8.2.1` |
| 7.0 en 7.1 | **2.6.2** | Tag `2.6.2` |

Voor Android 6 en ouder bevat deze selectie geen officieel aangewezen versie.
Een lagere `minSdk` in een oude APK is op zichzelf geen bewijs dat die versie
volgens de huidige AAPS-versiecontrole de aangewezen versie is.

De release notes vermelden dat voor oudere Android-versies aparte oude versies
zijn aangewezen met aangepaste versiecontrole. Daarom wordt bijvoorbeeld voor
Android 9–10 de actuele branch `v3.2.0.4` gebruikt en niet alleen de oorspronkelijke
tag met dezelfde versienaam. De ingebouwde versiecontrole wordt niet uitgeschakeld.
De huidige [upstream-versiedefinitie](https://github.com/nightscout/AndroidAPS/blob/versions/definition.json)
vermeldt voor `3.3.2.1` een einddatum van **30 september 2029**. Die definitie kan
later veranderen; dit overzicht is een controle op de bovenstaande datum, geen
belofte dat een release onbeperkt geldig blijft.

## Kanaalsnapshots

Naast de stabiele tag en bovenstaande vier versies worden de huidige standen
van **master**, **dev** en **dev3** klaargezet. Op de controledatum bevatten master
en dev3 versie **3.4.2.6** en dev versie **4.0.0-dev-c**. Alle drie hebben momenteel
Android **12 of nieuwer** nodig. Kanaalsnapshots krijgen het prerelease-label;
de Android-keuzetabel verwijst naar de stabiele en oude aangewezen versies.

## Bouwen en downloaden

De exacte commits staan in `.github/selected-releases.json`. **Seed Selected Releases**
bouwt alleen deze acht geselecteerde snapshots en slaat gepubliceerde releases over.
Dit is een eenmalige aanvulling op de automatische kanalen; de oorspronkelijke
baseline en uitsluiting van de volledige releasehistorie blijven intact.

De downloadbestanden verschijnen bij [GitHub Releases](https://github.com/smokkelaar/AndroidAPSversion/releases).
Elke voltooide release bevat een APK voor de telefoon en voor Wear, met dezelfde
ondertekening als je bestaande APK. De Android-eis voor Wear kan anders zijn dan
die voor de telefoon. Oude versies zijn afhankelijk van oude buildrepositories;
een vermelding in deze selectie betekent pas een downloadbare build zodra de
bijbehorende workflow en ondertekening zijn geslaagd.

## Resultaat van de historische bouwcontrole

De eerste [bouwcontrole van 3 oktober 2026](https://github.com/smokkelaar/AndroidAPSversion/actions/runs/37113752338)
liep voor Android 7 en 8 vast op verdwenen buildplugins en bibliotheken.
De herstelroute staat beschreven in [legacy-build/README.md](legacy-build/README.md),
inclusief broncommits, controlesommen en de volledige Gradle-patch voor Android 7.

- **Android 8 — AAPS 2.8.2.1:** [herstelde prerelease](https://github.com/smokkelaar/AndroidAPSversion/releases/tag/legacy-2.8.2.1-android-8-fb9325384e96).
  Gebouwd, ondertekend en gepubliceerd in [de herstelbuild](https://github.com/smokkelaar/AndroidAPSversion/actions/runs/37118312401).
- **Android 7 — AAPS 2.6.2:** [herstelde prerelease](https://github.com/smokkelaar/AndroidAPSversion/releases/tag/legacy-2.6.2-android-7-03ce42fc4c8e).
  Gebouwd, ondertekend en gepubliceerd in [de Android 7-herstelbuild](https://github.com/smokkelaar/AndroidAPSversion/actions/runs/37118781152).

Android 9–10 (**3.2.0.4**) en Android 11 (**3.3.2.1**) zijn eveneens beschikbaar
in GitHub Releases. Iedere gepubliceerde selectie bevat afzonderlijke APK's voor
telefoon en Wear. Herstelde Android 7/8-builds krijgen een prerelease-label.

De herstelroute vervangt verdwenen UI-bibliotheken door op SHA-256 vastgelegde
bestanden en verwijdert uit de Android 7-Gradle-configuratie alleen de verdwenen
Fabric- en Jacoco-buildplugins. De oorspronkelijke doseringscode, Android-eisen
en versiecontrole blijven intact. WearPreferenceActivity komt uit een externe
Appodeal-archiefkopie zonder door de auteur gepubliceerde checksum; onafhankelijke
byte-identiteit met het oorspronkelijke bestand is niet bewezen. Ondertekening
met hetzelfde certificaat en de minimale Android-versie worden door de workflow
gecontroleerd. Deze bouwcontrole omvat geen installatie- of werkingstest op een
fysieke telefoon of smartwatch.
