# demon_hill

<!--
#field
CTF

#groups
Tool

#languages
Python

#frames and libs

-->

<div align="center">
  <img src="img/logo.png" style="width: 40%"/>
</div>

## Info

Demon Hill is a cutsom proxy used in AD-style CTF's.
It recives packets from clients and send the to the server applyng "filters" between the connection; it can also reload itself via command.

## Filters

The filters are two lists (one for client data and one for server data) that contains functions that can operate on the data.

## Reload

It is initialized as only a main that imports himself like a module, and with the command "r" in the cmd when running, can reimport itself and reload new patches and filters to new and old connections without disconnect none.
