<h1 id="webui">WebUI</h1>

![Sample](https://user-images.githubusercontent.com/81442784/211213577-1323ff6a-4214-4540-96cf-0b4b39d02c09.png)

<h1 id="dependencies">Install Nextcloud</h1>
<div class="snippet-clipboard-content notranslate position-relative overflow-auto" data-snippet-clipboard-copy-content="curl -sSL https://raw.githubusercontent.com/nextcloud/nextcloudpi/master/install.sh | sudo bash"><pre class="notranslate"><code>curl -sSL https://raw.githubusercontent.com/nextcloud/nextcloudpi/master/install.sh | sudo bash</code></pre></div>

<h1 id="dependencies">Python Dependencies</h1>
<ul>
<li>flask</li>
<li>wifi</li>
<li>sounddevice</li>
<li>soundfile</li>
<li>pydub</li>
<li>selenium</li>
<li>msgraph_core</li>
<li>python-msgraph</li>
<li>msal</li>
</ul>
sudo apt-get install libportaudio2

<div class="snippet-clipboard-content notranslate position-relative overflow-auto" data-snippet-clipboard-copy-content="sudo pip3 install -r ~/Wedding-Audio-Book/requirments.txt"><pre class="notranslate"><code>sudo pip3 install -r ~/Wedding-Audio-Book/requirments.txt</code></pre></div>
<div class="snippet-clipboard-content notranslate position-relative overflow-auto" data-snippet-clipboard-copy-content="sudo apt-get install libportaudio2"><pre class="notranslate"><code>sudo apt-get install libportaudio2</code></pre></div>
<div class="snippet-clipboard-content notranslate position-relative overflow-auto" data-snippet-clipboard-copy-content="sudo apt-get install chromium-chromedriver"><pre class="notranslate"><code>sudo apt-get install chromium-chromedriver</code></pre></div>

<h1><a id="user-content-important" class="anchor" aria-hidden="true" href="#important"><svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg></a>PiSugar 3 Series Usage</h1>
<ul>
<li>
<p>This software will occupy i2c addresses 0x32(RTC) and 0x75(PowerIC). Please avoid other phats using these addresses.</p>
</li>
<li>
<p>We had upgradged PiSugar2 to new model. To identify it, please check the charging indicate led count, 4-leds is for old model, 2-leds is for new model. The new model is able to accurately detected the charging status and control the charging recycle.</p>
</li>
</ul>
<p>After attaching PiSugar2 to you pi, you can use the following commands to see whether it works properly:</p>
<div class="snippet-clipboard-content notranslate position-relative overflow-auto" data-snippet-clipboard-copy-content="# turn on i2c interface
sudo raspi-config

# Interfacing Options -&gt; I2C -&gt; Yes

<h2>detect i2c bus and devices</h2>
<pre class="notranslate"><code># turn on i2c interface
sudo raspi-config
i2cdetect -y 1
i2cdump -y 1 0x32
i2cdump -y 1 0x75
</code></pre></div>

<p>If you cannot find any devices, or see lots of 'X.XX.X.X...' things, please try turning off PiSugar 2 and restart one minutes later.</p>
<h2><a id="user-content-installation" class="anchor" aria-hidden="true" href="#installation"><svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"></path></svg></a>Installation</h2>
<p>Run the following script on your pi:</p>
<div class="snippet-clipboard-content notranslate position-relative overflow-auto" data-snippet-clipboard-copy-content="curl http://cdn.pisugar.com/release/pisugar-power-manager.sh | sudo bash"><pre class="notranslate"><code>curl http://cdn.pisugar.com/release/pisugar-power-manager.sh | sudo bash
</code></pre></div>
<p>After finished, you can manage the battery by visiting http://&lt;your raspberry ip&gt;:8421 in your browser.</p>
<p>
