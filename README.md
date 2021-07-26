
TL;DR - check out the app [here](https://share.streamlit.io/tapaco/marametrics/app.py). 

![bathalf.jpeg](/media/bathalf.jpeg)

As a nod to Michael Lewis' [Moneyball](https://www.amazon.co.uk/Moneyball-Art-Winning-Unfair-Game/dp/0393324818), I wanted to find a way to gauge my running efforts and see if crunching the numbers could point to some sort of ‘edge’. In this post, I describe my thought process, how I explored the data and deployed my insights as a dashboard using Streamlit. 

As an avid Strava user, sure I could just upgrade to a premium subscription and instantly get some cool stats, but where's the fun in that? I felt their proprietary calculations were too abstract for my liking and instead I opted to have a shot at estimating metrics used by pro athletics coaches (like VO2 Max). 

The recipe for this app:

- [Getting the data](#getting-the-data)
- [Transforming the data](#transforming-the-data)
- [Plotting the data](#plotting-the-data)
- [Building the app](#building-the-app)

## Getting the data

At first, I tried getting the raw data directly from my Garmin smart watch with no luck. Fortunately, Strava have a well documented [API](https://developers.strava.com/docs/getting-started/) where you can grab all your uploaded activities. To access anything through the API, be aware that you first need to use your '**refresh**' token, which then obtains a temporary '**access**' token (valid only for a few hours). By packaging these two in a GET request, this is the only way to return each activity as a JSON file. Franchyze923 has a great series of [videos](https://www.youtube.com/watch?v=sgscChKfGyg) explaining this in more detail in case you get stuck. 

As I had no clue about the kind of data coming at me from the API requests, I used a Jupyter notebook (hosted on [SageMaker](https://aws.amazon.com/sagemaker/)) to play with the data first, before any further parsing or app development. 

The requests returned a huge range of interesting metrics for each activity, with some vital (like speed) and some peculiar (an encoded polyline which can be used to trace your activity on Google Maps - see below).

![polyline.png](/media/polyline.png)

## Transforming the data

After filtering for only running activities, the parameters I wanted to analyse were the distance, moving time, cadence (steps per minute), total elevation gain, heartrate and speed (metres per second). I converted the latter into the more commonly used 'pace' measurement - minutes per kilometre. 

More recently, cadence stood out for me as some runs have left my shins aching, so I'm keen to track and push my cadence above the optimum of 180 steps per minute to ensure that my strides are efficient and minimise the risk of injuries, as highlighted by [Sweat Science](https://www.outsideonline.com/2377976/stop-overthinking-your-running-cadence).

![manny.jpeg](/media/manny.jpeg)

In addition to these base metrics, I wanted to calculate two metrics used by the pros - VO2 Max and Running Power. 

VO2 Max is the maximum amount of oxygen absorbed by the body during the workout and gives a good estimate of overall fitness. 

Power is the amount of energy produced by the work done during running, estimating the efficiency of my runs and the load on my muscles. They both typically fluctuate depending on the type of workout. 

Both of these metrics are usually calculated in state-of-the-art sports labs but fortunately [The Secret of Running](https://hetgeheimvanhardlopen.nl) have fantastic articles on how to estimate them with simple formulae - [VO2 Max](https://hetgeheimvanhardlopen.nl/en/what-is-wrong-with-the-garmin-race-predictor-supplemented-version/) and [Power](https://hetgeheimvanhardlopen.nl/en/translate-your-workout-description-in-running-power-yourself/). 

## Plotting the data

Any dashboard needs decent visuals to demonstrate insights. My app uses three - the *k*-means preview, the radar chart and the time trend plot - each of which have distinct roles. 

First up, a preview of the data that has been clustered by *k*-means. As I didn't manually label each of my runs as a jog/workout/race, I ran a *k*-means clustering algorithm (a form of unsupervised machine learning) on the data. The reason for this was to quickly group similar runs into '*k*' distinct buckets (or clusters), which would make it easier to spot differences within a cluster of chilled jogs or tempo runs for example.

Next, a radar chart showing the last 3 runs using the Plotly library. This visualisation makes it easy to eyeball data by standardising five key metrics (distance, elevation, heartrate, speed and VO2 Max) on a scale from 1 to 5. This allows for quick comparisons between the last three runs by plotting a snazzy polygon for each run. 

![radarchart.png](/media/radarchart.png)

Finally, a trend plotting how pace and heartrate vary over time again using Plotly. I use my heartrate as a proxy for how difficult I found a workout and I wanted to compare this to how my pace varies as a result. The time trend element allows me to understand whether I have been able to maintain my goal of running at a faster pace at a lower heartrate (i.e. running faster with less effort). 

![timetrend.png](/media/timetrend.png)

## Building the app

So all this cleaning, analysis and charting - now what? 

[Streamlit](https://streamlit.io) is the secret sauce that binds all these together as an app, all using Python which I perfect as I'm allergic to JavaScript. 

Into a fresh Python script, I simply copied the visualisations I wanted from my Jupyter notebook and added some widgets to allow users to tweak the clustering. All functions to obtain or clean the data are imported from a separate script. 

![app.png](/media/app.png)

Thom Lane provides a kickass AWS CloudFormation [template](https://github.com/awslabs/sagemaker-dashboards-for-ml) to deploy the app into containers, which is complete with auto-scaling and can be done in a few clicks.
