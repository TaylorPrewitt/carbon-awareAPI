import React from 'react';
import './KbSummary.css'

const KbSummary = () => {

    return(    
        <div>
            <div className="body">
                <h1>Azure Carbon API: Knowledge Base Overview</h1>
                <p><em>Taylor Prewitt |  Max Weil |  Amruta Jadhav |  Shivang Dalal | Thet Noe | Larry Tian | Maynard Maynard-Zhang | Kevin Yip | Divij Satija</em></p>
                <h2>Introduction</h2>
                <p>
                    Since the start of the First Industrial Revolution, more than 2 trillion metric tons of greenhouse 
                    gases have been released into the atmosphere by humans. Three-quarters of these emissions are carbon dioxide, 
                    and the amount of carbon dioxide already exceeds the amount that nature can re-absorb (Smith, 2020). Global 
                    temperatures are rising as carbon in the atmosphere forms a layer of heat-trapping gases. According to NOAA 
                    National Centers for Environmental Information’s 2020 Global Climate Report, “the combined land and ocean 
                    temperature has increased at an average rate of 0.13 degrees Fahrenheit”, and this rate has doubled since 1981 (Lindsey &amp; Dahlman, 2021).
                </p>
                <p>&nbsp;</p>
                <figure>
                    <div>
                        <img className="image" src='https://news-media.stanford.edu/wp-content/uploads/2019/04/17105725/Inequality3.jpg' alt="Figure 2"/>
                        <figcaption><em>Figure 1. Recent Temperature Trends (1990 - 2019)</em></figcaption>
                    </div>
                </figure>

                <p>If we do not reduce emissions and temperatures continue to rise, science predicts that the consequences will be disastrous (Buis, 2019).</p>
                <p>
                    As one of the most advanced technology companies in the world, Microsoft has decided to be Carbon Negative by 2030. 
                    To achieve this goal, Microsoft needs to develop new technologies that allow suppliers and customers to use more energy 
                    while reducing their carbon footprints (Smith, 2020). While this goal is a bold bet, it is achievable if people harness the power of 
                    data science, artificial intelligence, and digital technology. The project's goal is to use Watttime data to create a carbon emission 
                    calculator that will assist users in calculating the carbon impact of their applications and determining the most cost-effective use 
                    of carbon. This report acts as a succinct overview of the knowledge base created during the research for this project.
                </p>
                <p>
                    As the world economy has grown, so has the energy consumption. As a result, carbon emissions have steadily risen, 
                    and they will continue to rise if this trend continues.
                </p>
                <figure>
                    <div>
                        <img className="image" src='https://raw.githubusercontent.com/ThetNoe/PicForMarkDown/main/figure2.png' alt="Figure 2" />
                    </div>
                </figure>
                <p>
                    This is problematic because the increase in CO2 has been the primary contributor to the rise in global temperature. 
                    In the United States, the electricity system is the largest single source of carbon emissions (Mandel, 2016). 
                    As one of the large consumers of electricity, Microsoft plays an important role in tackling carbon-caused climate change.
                </p>
                <p>As outlined in <a href="https://www.theclimatepledge.com/">The Climate Pledge</a>, there are three accepted strategies for successfully managing carbon emissions:</p>
                
                <ol>
                    <li><strong>Regular reporting</strong> - measuring and reporting emissions regularly to ensure transparency and accountability</li>
                    <li><strong>Carbon elimination</strong> - implementing carbon reduction strategies, including increasing efficiency, using renewable energy, and reducing materials usage</li>
                    <li><strong>Credible offsets</strong> - investing in “additional, quantifiable, real, permanent, and socially beneficial” offsets</li>
                </ol>
                <p>
                    While regular reporting and offsetting are important, this project primarily focuses on carbon elimination to decarbonize future energy 
                    consumption. Specifically, this project aims to build a Carbon API that allows customers—businesses who utilize Microsoft Azure—to quickly
                     and effectively calculate the carbon impact of their application. This API will exist as a wrapper on top of the WattTime API that makes 
                     calculations based on variables such as the time of day and the power source. This API will empower consumers to make more informed and
                      environmentally-conscientious decisions. This project directly aligns with several of Microsoft’s 
                      <a href="https://blogs.microsoft.com/blog/2020/01/16/microsoft-will-be-carbon-negative-by-2030/">‘Carbon Negative by 2030’ plan</a> principles:
                </p>

                <ul>
                    <li>Principle 1: Grounding in science and accurate math</li>
                    <li>Principle 2: Taking Responsibility for Our Carbon Footprint</li>
                    <li>Principle 4: Empowering Customers around the World</li>
                </ul>
                <p><strong><em>Ultimately, this Carbon API will succeed as a complement to Microsoft’s existing strategies for driving down carbon emissions.</em></strong></p>      

                <h2>Grounding in Science and Accurate Math</h2>
                <p>
                    When it comes to strategizing carbon reduction plans to combat climate change, the most vital and the very first 
                    step is knowing how to use the accurate “carbon math” to manage emissions effectively. Unlike any other metric, 
                    carbon metrics can be extremely complex to calculate accurately. That’s why many big corporations like Google and Microsoft, 
                    which are the current leaders moving toward the sustainable future, are making the most accurate carbon math as one of the core principles of 
                    their company climate pledges. To improve accuracy of their carbon calculations, Google has even developed a new metric called the
                     carbon-free energy percentage (CFE%), which represents the average percentage of carbon free energy consumed in a particular location on 
                     an hourly basis.
                </p>
                <p>
                    Within the effort of calculating the most accurate “carbon math”, the most common mistake found in many organizations 
                    is the use of average and marginal emissions in the wrong context. In order to understand the difference between average 
                    and marginal emissions of the electricity system, understanding today’s competitive energy wholesale market is required.
                </p>
                <p>
                    Up until 20 years ago, a single utility was responsible to dial-up and down its daily energy supply for a specific area
                     depending on the demand. It would own the power plant (power source) and all the transmission lines that are necessary 
                     to supply power. However, in today’s energy market, all the resources are shared and administered by organizations like CAISO.
                      The market does a short-term demand forecast a day ahead to bring in enough suppliers to come online and place bids (Liastgarten, 2019). 
                      As seen in figure below, all the power plants are brought in order of price and every five minutes throughout the day, the market decides 
                      which plant to run, to match the supply.
                </p>
                <figure>
                    <div>
                        <img className="big_image" src='https://www.iso-ne.com/static-assets/img/how-prices-are-set-2018-01.jpg' alt="Figure 3"/>
                    </div>
                </figure>

                <h2>Average Emissions &amp; Marginal Emissions</h2>
                <p>
                    <strong>Average emissions</strong> are calculated across all generators by using the total carbon emission and total amount of electricity generated.  
                    Referring back to the supply stack above, the average emissions would be the average of plant A, B, C, and part of D. Google uses average emission 
                    for <a href="https://www.zdnet.com/article/how-clean-is-cloud-computing-new-data-reveals-how-green-googles-data-centers-really-are/">CFE%</a> calculations. 
                    This value can indicate which regions are performing at optimal levels for lessening their carbon impacts and which regions need significant improvement 
                    in renewable energy systems. In addition, the CFE% allows Google to inform its customers about optimal locations to provide services across their cloud 
                    infrastructure. Other than costs and data latency, carbon emissions are also important when determining the location to run an application. 
                    For example, in the state of Oregon, the calculated CFE% is 89%, which means that on average, the data centers in Oregon run on carbon free energy 
                    about 89% of the time.
                </p>
                <p>
                    <strong>Marginal emissions</strong> are calculated  based on the relationship between decision and consequence. 
                    (Corradi, 2019) “The marginal emissions are the emissions that would come online if new loads were added.”( Listgarten, 2019). 
                    According to the supply stack above, the marginal emissions are from plant D. Due to its predictive nature of carbon intensity 
                    on the grid, it’s more accurate for loadshiting, scheduling and optimizing a flexible load with a cleaner energy. According to 
                    <a href="https://gridbeyond.com/load-shifting-low-down-guide/">GridBeyond</a>, <strong>load shifting</strong> essentially means 
                    moving electricity consumption or electric loads from one time period or region to another.
                </p>

                <h2>Marginal Emissions for Load shifting</h2>
                <p>
                    Compared to average emissions, marginal emissions are more accurate for optimizing and scheduling load shifting to help reduce our
                    emissions. To explain loadshifting, assume that there are three different power plants on the grid as shown below - solar (10MW capacity) , 
                    efficient gas (10MW capacity) and inefficient gas (4MW capacity). Solar plant A has zero carbon emissions, coal gas plant B has medium emissions, 
                    and coal gas plant C has high emissions.
                </p>

                <figure>
                    <div>
                        <img className="image" src='https://www.paloaltoonline.com/blogs/photos/44/3354.jpg' alt="Figure 2" />
                        <figcaption><em>Source: <a href= "https://www.paloaltoonline.com/blogs/p/2019/09/29/marginal-emissions-what-they-are-and-when-to-use-them">Palo Alto</a></em></figcaption>
                    </div>
                </figure>

                <p>
                    These three power plants run to meet the demand of 5 MW at 1 AM and 21 MW at 4 PM. The average emissions will be lower at 4 PM since 
                    average emission is calculated across all power plants and the solar plant A will bring down the average emissions. However, 
                    the marginal emissions are lower at 1 AM. Therefore, if a flexible load is to be scheduled to help reduce the emissions, marginal 
                    emissions should be used and scheduled for 1 AM. Doing this will make the requirements to be met by the efficient gas plant 
                    B that has medium emissions instead of inefficient gas with high CO2. 
                </p>

                <p>
                    When considering how a hyer-scale computing should geographically shift their computing load to reduce CO2 emissions from electric 
                    power generation, studies have found that shifting based on the marginal emissions achieves a significant reduction in CO2 and 
                    outperforms shifting based on average emissions. (Lindberg et al., 2020). Figure below shows the result of Google’s tests on load-shifting 
                    at data centers with its new carbon-intelligence computing platform based on marginal emissions. 
                </p>

                <figure>
                    <div>
                        <img className="image" src='https://storage.googleapis.com/gweb-uniblog-publish-prod/images/BINK_carbonaware_linegraph_1.max-600x600.jpg' />
                        <figcaption><em>Source: <a href= "https://blog.google/inside-google/infrastructure/data-centers-work-harder-sun-shines-wind-blows">Google </a></em></figcaption>
                    </div>
                </figure>

                <h2>Limitation of Marginal Emissions</h2>
                <p>
                    However, unlike average emissions, marginal emissions are not easily available and extremely volatile. 
                    A good example can be the one given by Listgarten (2019).
                </p>
                <img className="big_image" alt="this is Alt Text" src="https://github.com/ThetNoe/PicForMarkDown/blob/main/Supply.png?raw=true" />
                <figcaption><em>Source: <a href= "https://blog.google/inside-google/infrastructure/data-centers-work-harder-sun-shines-wind-blows">CAISO </a> </em></figcaption>

                <p>
                    The graph above shows the energy supply on May 3rd, 2019. At 1:27 PM on that day, the average emissions were 284 lbs/MWh and 
                    marginal emissions were 1012lbs/MWh. There is a considerable amount of difference between average and marginal emission. 
                    This was caused by a sudden drop in solar and rise of natural gas at 1:27PM. At around 1:50PM, the solar came back up and marginal 
                    emissions dropped again. Even within a 30-minute time frame, marginal emissions are hard to predict and volatile.Just like many other 
                    companies today, which are committed to move toward a sustainable future and greener energy, Microsoft and its Carbon ‘Carbon Negative 
                    by 2030’ plan principles are invested in science, technology and accurate math to reduce and remove the company’s historical carbon emissions. 
                    Today, thanks to many new technological solutions and accurate metrics, we can accurately measure carbon emissions to better strategize our 
                    emission reduction efforts. For example, companies can now utilize advanced technological tools like WattTime’s Automated Emission Reduction 
                    (AER) technology to lower the emission by automatically scheduling their load with cleaner energy and avoid dirtier energy without compromising 
                    performance and cost.
                </p>      
            </div>
        </div>
    );
}

export default KbSummary; 