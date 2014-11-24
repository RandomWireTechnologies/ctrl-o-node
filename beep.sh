#!/bin/bash

gpio=/usr/local/bin/gpio


tone (){
  local note="$1" time="$2"
  if test "$note" -eq 0; then
    $gpio -g mode 18 in
  else
    local period="$(perl -e"printf'%.0f',600000/440/2**(($note-69)/12)")"
    $gpio -g mode 18 pwm
    $gpio pwmr "$((period))"
    $gpio -g pwm 18 "$((period/2))"
    $gpio pwm-ms
  fi
  sleep "$time"
}

playxmas(){
 tone 63 0.2
 tone 63 0.2
 tone 63 0.3
 tone 0 0
 tone 0 0
 tone 0 0
 tone 63 0.2
 tone 63 0.2
 tone 63 0.3
 tone 0 0
 tone 0 0
 tone 0 0
 tone 63 0.2
 tone 65 0.2
 tone 61 0.3
 tone 62 0.1
 tone 63 0.6
 tone 0 0
}

shave(){
	tone 61 0.2
	tone 56 0.1
	tone 56 0.1
	tone 58 0.2
	tone 56 0.2
	tone 0 0.2
	tone 60 0.2
	tone 61 0.2
	tone 0 0
}

beep(){
	tone 107 0.2
	tone 0 0

}

beep
