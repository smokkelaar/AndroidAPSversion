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

In de [bouwcontrole van 3 oktober 2026](https://github.com/smokkelaar/AndroidAPSversion/actions/runs/37113752338)
is **3.2.0.4 voor Android 9–10** succesvol gebouwd, ondertekend en gepubliceerd.
**3.3.2.1 voor Android 11** is eveneens beschikbaar in GitHub Releases.

De twee oudste geselecteerde versies zijn nog niet downloadbaar als APK:

- **2.8.2.1 / Android 8:** de oorspronkelijke afhankelijkheden
  `com.google.android:flexbox:0.3.0` en
  `com.amulyakhare:com.amulyakhare.textdrawable:1.0.1` konden niet worden opgehaald.
- **2.6.2 / Android 7:** de oorspronkelijke buildplugin
  `io.fabric.tools:gradle:1.31.2` kon niet worden opgehaald; de Fabric-server gaf HTTP 403.

Dit zijn bouwbeperkingen en veranderen de officiële Android-keuzetabel niet.
De oorspronkelijke broncode, afhankelijkheidsversies en geldigheidscontroles
zijn behouden. Een herstel van deze historische toolchains is nog nodig voordat
voor Android 7 en 8 een ondertekende APK kan worden gepubliceerd.
