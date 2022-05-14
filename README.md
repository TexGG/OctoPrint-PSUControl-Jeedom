# OctoPrint PSU Control - Jeedom
Adds Jeedom support to OctoPrint-PSUControl as a sub-plugin

## Setup
- Install the plugin using Plugin Manager from Settings
- Configure this plugin
- Select this plugin as Switching *and* Sensing method in [PSU Control](https://github.com/kantlivelong/OctoPrint-PSUControl)
- **Turn off** the *Automatically turn PSU ON* option in the PSU Control settings, leaving this on will ruin your prints when Jeedom becomes unavailable

## Configuration
* Enter the URL of your Jeedom Installation
* Go to your Jeedom profile
* Go on the *API* tab
* Copy the API key and paste it into the *Api key* field in the plugin settings
* At *"On" CMD ID* enter the ID of command you want to call. You can find it by going on the device selecting the *Commands* tab. There, you search the *On* command, copy the *ID/#* on the left and past it in the corresponding field.
* At *"Off" CMD ID* enter the ID of command you want to call. You can find it by going on the device selecting the *Commands* tab. There, you search the *On* command, copy the *ID/#* on the left and past it in the corresponding field.
* At *"Status" CMD ID* enter the ID of command you want to call. You can find it by going on the device selecting the *Commands* tab. There, you search the *On* command, copy the *ID/#* on the left and past it in the corresponding field.
* If your HA installation is running HTTPS with a self-signed certificate, uncheck the *Verify certificate* option

## Support
Please check your logs first. If they do not explain your issue, open an issue in GitHub. Please set *octoprint.plugins.psucontrol* and *octoprint.plugins.psucontrol_jeedom* to **DEBUG** and include the relevant logs. Feature requests are welcome as well.

## Todo
- [ ] Add images to documentation