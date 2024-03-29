<div align="center">

# cryptocurrency-trading-by-shadow

Automated trading program for cryptocurrency by shadow :chart_with_upwards_trend:

<a href="https://ubuntu.com/" target="_blank">
  <img width="90" alt="ubuntu-logo" src="https://user-images.githubusercontent.com/42294938/136695374-bf08e2da-217f-4a5e-ad75-f97b58d01fa6.png" />
</a>

<a href="https://www.docker.com/" target="_blank">
  <img width="120" alt="Docker-logo" src="https://user-images.githubusercontent.com/42294938/136694984-5897ffef-afef-49fb-95a1-3a1fe376cbe3.png" />
</a>
<a href="https://www.anaconda.com/" target="_blank">
  <img width="110" alt="Anaconda-logo" src="https://user-images.githubusercontent.com/42294938/136695102-ff45bc3c-98ff-4a7d-ba84-d1f4cb1bb30e.png" />
</a>

<a href="https://jupyterlab.readthedocs.io/" target="_blank">
  <img width="100" alt="JupyterLab-logo" src="https://user-images.githubusercontent.com/42294938/136695067-c278fdd9-f3fa-49fd-a981-2bbccc3e9293.png" />
</a>
</div>

## :hammer_and_wrench: Stack

- ubuntu
- Docker
- Anaconda
  - JupyterLab

## :fire: Supported Exchanges

- GMO

## :star2: About Logic

The logic is to place a limit order in front of a thick board of sellers and buyers and catch the whiskers.</br>

<div align="center">
  <img width="700" alt="JupyterLab-logo" src="https://user-images.githubusercontent.com/42294938/137625602-e63d3ecf-334c-4e01-a2ad-4cd6b7dd99e2.jpg" />
</div>

### 1. Grouping

Fewer orders on the GMO board, so group them together

### 2. Order

Find a large size order in the grouped board and place a limit order in front of it.

The price of the limit order is the largest amount before the grouping.

### 3. Close Order

If the buy or sell order is executed after 5 seconds, the settlement order is submitted.

Cancel all orders that have not been executed.
