# Eventghost-Sony-TV-Network-Remote-Plugin-2023

This is an Eventghost plugin for IP-based Sony TV's, probably starting with 2013 or earlier and extending to at least 2023.

It is based on the plugin archived at https://github.com/dequi/eventghost-general-PluginDatabase/tree/master/Sony%20TV%20Network%20Remote%20Plugin/0.0.2

Changes made to the original IRCC-only plugin are:

1.) Fixed bug that didn't allow the IP address and pre-shared key to be set via the dialog box.  The hardcoded defaults would always be used instead of the one's set.
2.) Added Simple IP control event.  No built-in presets; the command strings must be gotten from here: https://pro-bravia.sony.net/develop/integrate/ssip/command-definitions/index.html
3.) Added REST control event.  No built-in presets; the "service" and "command" strings must be gotten from here: https://pro-bravia.sony.net/develop/integrate/rest-api/spec/index.html - Note that for a random reason, the REST control strings of "service" and "command" are all contained in a single, one-line command string.  First comes the service name (like "audio" or "system"), then a space, and then the JSON REST command w/o any newlines.
