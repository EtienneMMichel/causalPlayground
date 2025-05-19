# Causal PLAYGROUND

## CONFIGURE
An example of config file:

```yaml
mode: discover_from_prices_and_volume

data:
  symbols: ["BTC_USDT", "ETH_USDT", "SOL_USDT"]
  timeframe: "1m"
  start_date: "07-2024"
  end_date: "08-2024"
  window: 60

model:
  name: PCMCI
  alpha_level: 0.1
  tau_max: 5
  pc_alpha: 0.05
  independence_test:
    name: ParCorr
    args:
      significance: analytic
```


## RUN
```bash
virtualenv venv
. venv/Scripts/activate
python main.py config.yaml
```