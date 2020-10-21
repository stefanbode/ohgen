Thing mqtt:topic:mosquitto:{{thingid}} "{{label}}" (mqtt:broker:mosquitto) {
    Channels:
        Type switch : power	     [ stateTopic="hm/status/{{thingid}}/RESULT", transformationPattern="REGEX:(.*POWER.*)∩JSONPATH:$.POWER", commandTopic="cmnd/{{thingid}}/POWER" ]
        Type dimmer : dimmer     [ stateTopic="hm/status/{{thingid}}/RESULT", transformationPattern="REGEX:(.*Dimmer.*)∩JSONPATH:$.Dimmer", commandTopic="cmnd/{{thingid}}/Dimmer" ]
        Type switch : sw1_stat   [ stateTopic="hm/status/{{thingid}}STATUS11",transformationPattern="JSONPATH:$.StatusSTS.POWER1",on="ON",off="OFF"] 
        
        
{%- if 'ct' in features %}
        Type dimmer : ct         [ stateTopic="hm/status/{{thingid}}/RESULT", transformationPattern="REGEX:(.*CT.*)∩JSONPATH:$.CT", commandTopic="cmnd/{{thingid}}/CT", min=153, max=500, step=1 ]
{%- endif -%}

{%- if 'color' in features %}
        Type string : color      [ stateTopic="hm/status/{{thingid}}/RESULT", transformationPattern="REGEX:(.*Color.*)∩JSONPATH:$.Color", commandTopic="cmnd/{{thingid}}/Color" ]
        Type colorHSB : colorhsb [ stateTopic="hm/status/{{thingid}}/RESULT", transformationPattern="REGEX:(.*HSBColor.*)∩JSONPATH:$.HSBColor", commandTopic="cmnd/{{thingid}}/HSBColor" ]
{%- endif %}
        Type switch : reachable	 [ stateTopic="hm/settings/{{thingid}}/LWT", on="Online", off="Offline" ]
        Type number : rssi	     [ stateTopic="hm/settings/{{thingid}}/STATE", transformationPattern="JSONPATH:$.Wifi.RSSI" ]
        Type string : state      [ stateTopic="hm/settings/{{thingid}}/dummy", commandTopic="cmnd/{{thingid}}/STATE" ]
}

Switch {{name}}_Power  "{{label}} Power" <light> {{groups|groups}}{{tags|tags}} { channel="mqtt:topic:mosquitto:{{thingid}}:power", autoupdate="false" }
Dimmer {{name}}_Dimmer {{label|quote}} { channel="mqtt:topic:mosquitto:{{thingid}}:dimmer"{{ metadata|metadata }} }
{% if 'ct' in features -%}
Dimmer {{name}}_CT     "{{label}} CT"            { channel="mqtt:topic:mosquitto:{{thingid}}:ct" }
{% endif -%}
{% if 'color' in features -%}
String {{name}}_Color  "{{label}} Color"  { channel="mqtt:topic:mosquitto:{{thingid}}:color" }
{% endif -%}
Number {{name}}_RSSI   "{{label}} RSSI [%d%%]" <network> (gSignalStrength) { channel="mqtt:topic:mosquitto:{{thingid}}:rssi" }
String {{name}}_State (gTasmotaState)     { channel="mqtt:topic:mosquitto:{{thingid}}:state" }
