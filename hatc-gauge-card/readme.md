# HATC-GAUGE-CARD

## Description

....

### Fonctionnalité
- 1
- 2

### Fonctionnalité futures
- 1
- 2

## Options
| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| type | string | **Obligatoire** | `custom:hatc-gauge-card` |
| entity | string | **Obligatoire** | `sensor.processor_temperature` |
| [Gauge](#gauge-options) | object | x | x |

## Gauge Options

## Examples

#### Default

```yaml
type: custom:hatc-gauge-card
entity: sensor.temperature_moyenne_hall_d_entree

title: Titre de la carte

gauge:
  max_value: 50 
  text-color: severity
  friendly_name: false
  unit_of_measurement: false
  severity:
    - color: blue
    - color: yellow
      from: 20
      to: 22
    - color: orange
      from: 22
      to: 24
    - color: red
      from: 24
      to: 26
    - color: purple
      from: 26
      to: 28
    - color: deep-purple
      icon: mdi:xxx
      from: 28
      to: 50
```