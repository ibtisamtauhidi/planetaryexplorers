#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("""

                          <html>
<head>
<title>Planetary Explorers</title>
<meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">

<script type="text/javascript" src="./js/glMatrix-0.9.5.min.js"></script>
<script type="text/javascript" src="./js/webgl-utils.js"></script>
<script src="./js/jquery.js" type="text/javascript"></script> 

<script id="per-fragment-lighting-fs" type="x-shader/x-fragment">
    precision mediump float;

    varying vec2 vTextureCoord;
    varying vec3 vTransformedNormal;
    varying vec4 vPosition;

    uniform bool uUseColorMap;
    uniform bool uUseSpecularMap;
    uniform bool uUseLighting;

    uniform vec3 uAmbientColor;

    uniform vec3 uPointLightingLocation;
    uniform vec3 uPointLightingSpecularColor;
    uniform vec3 uPointLightingDiffuseColor;

    uniform sampler2D uColorMapSampler;
    uniform sampler2D uSpecularMapSampler;


    void main(void) {
        vec3 lightWeighting;
        if (!uUseLighting) {
            lightWeighting = vec3(1.0, 1.0, 1.0);
        } else {
            vec3 lightDirection = normalize(uPointLightingLocation - vPosition.xyz);
            vec3 normal = normalize(vTransformedNormal);

            float specularLightWeighting = 0.0;
            float shininess = 32.0;
            if (uUseSpecularMap) {
                shininess = texture2D(uSpecularMapSampler, vec2(vTextureCoord.s, vTextureCoord.t)).r * 255.0;
            }
            if (shininess < 255.0) {
                vec3 eyeDirection = normalize(-vPosition.xyz);
                vec3 reflectionDirection = reflect(-lightDirection, normal);

                specularLightWeighting = pow(max(dot(reflectionDirection, eyeDirection), 0.0), shininess);
            }

            float diffuseLightWeighting = max(dot(normal, lightDirection), 0.0);
            lightWeighting = uAmbientColor
                + uPointLightingSpecularColor * specularLightWeighting
                + uPointLightingDiffuseColor * diffuseLightWeighting;
        }

        vec4 fragmentColor;
        if (uUseColorMap) {
            fragmentColor = texture2D(uColorMapSampler, vec2(vTextureCoord.s, vTextureCoord.t));
        } else {
            fragmentColor = vec4(1.0, 1.0, 1.0, 1.0);
        }
        gl_FragColor = vec4(fragmentColor.rgb * lightWeighting, fragmentColor.a);
    }
</script>

<script id="per-fragment-lighting-vs" type="x-shader/x-vertex">
	attribute vec3 aVertexPosition;
	attribute vec3 aVertexNormal;
	attribute vec2 aTextureCoord;
	
	uniform mat4 uMVMatrix;
	uniform mat4 uPMatrix;
	uniform mat3 uNMatrix;
	
	varying vec2 vTextureCoord;
	varying vec3 vTransformedNormal;
	varying vec4 vPosition;
	
	
	void main(void) {
		vPosition = uMVMatrix * vec4(aVertexPosition, 1.0);
		gl_Position = uPMatrix * vPosition;
		vTextureCoord = aTextureCoord;
		vTransformedNormal = uNMatrix * aVertexNormal;
	}
</script>


<script type="text/javascript">
var gl;

function initGL(canvas) {
	try {
		gl = canvas.getContext("experimental-webgl");
		gl.viewportWidth = canvas.width;
		gl.viewportHeight = canvas.height;
	} catch (e) {
	}
	if (!gl) {
		alert("Could not initialise WebGL, sorry :-(");
	}
}


function getShader(gl, id) {
	var shaderScript = document.getElementById(id);
	if (!shaderScript) {
		return null;
	}

	var str = "";
	var k = shaderScript.firstChild;
	while (k) {
		if (k.nodeType == 3) {
			str += k.textContent;
		}
		k = k.nextSibling;
	}

	var shader;
	if (shaderScript.type == "x-shader/x-fragment") {
		shader = gl.createShader(gl.FRAGMENT_SHADER);
	} else if (shaderScript.type == "x-shader/x-vertex") {
		shader = gl.createShader(gl.VERTEX_SHADER);
	} else {
		return null;
	}

	gl.shaderSource(shader, str);
	gl.compileShader(shader);

	if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
		alert(gl.getShaderInfoLog(shader));
		return null;
	}

	return shader;
}


var shaderProgram;

function initShaders() {
	var fragmentShader = getShader(gl, "per-fragment-lighting-fs");
	var vertexShader = getShader(gl, "per-fragment-lighting-vs");

	shaderProgram = gl.createProgram();
	gl.attachShader(shaderProgram, vertexShader);
	gl.attachShader(shaderProgram, fragmentShader);
	gl.linkProgram(shaderProgram);

	if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
		alert("Could not initialise shaders");
	}

	gl.useProgram(shaderProgram);

	shaderProgram.vertexPositionAttribute = gl.getAttribLocation(shaderProgram, "aVertexPosition");
	gl.enableVertexAttribArray(shaderProgram.vertexPositionAttribute);

	shaderProgram.vertexNormalAttribute = gl.getAttribLocation(shaderProgram, "aVertexNormal");
	gl.enableVertexAttribArray(shaderProgram.vertexNormalAttribute);

	shaderProgram.textureCoordAttribute = gl.getAttribLocation(shaderProgram, "aTextureCoord");
	gl.enableVertexAttribArray(shaderProgram.textureCoordAttribute);

	shaderProgram.pMatrixUniform = gl.getUniformLocation(shaderProgram, "uPMatrix");
	shaderProgram.mvMatrixUniform = gl.getUniformLocation(shaderProgram, "uMVMatrix");
	shaderProgram.nMatrixUniform = gl.getUniformLocation(shaderProgram, "uNMatrix");
	shaderProgram.colorMapSamplerUniform = gl.getUniformLocation(shaderProgram, "uColorMapSampler");
	shaderProgram.specularMapSamplerUniform = gl.getUniformLocation(shaderProgram, "uSpecularMapSampler");
	shaderProgram.useColorMapUniform = gl.getUniformLocation(shaderProgram, "uUseColorMap");
	shaderProgram.useSpecularMapUniform = gl.getUniformLocation(shaderProgram, "uUseSpecularMap");
	shaderProgram.useLightingUniform = gl.getUniformLocation(shaderProgram, "uUseLighting");
	shaderProgram.ambientColorUniform = gl.getUniformLocation(shaderProgram, "uAmbientColor");
	shaderProgram.pointLightingLocationUniform = gl.getUniformLocation(shaderProgram, "uPointLightingLocation");
	shaderProgram.pointLightingSpecularColorUniform = gl.getUniformLocation(shaderProgram, "uPointLightingSpecularColor");
	shaderProgram.pointLightingDiffuseColorUniform = gl.getUniformLocation(shaderProgram, "uPointLightingDiffuseColor");
}


function handleLoadedTexture(texture) {
	gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
	gl.bindTexture(gl.TEXTURE_2D, texture);
	gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, texture.image);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_NEAREST);
	gl.generateMipmap(gl.TEXTURE_2D);

	gl.bindTexture(gl.TEXTURE_2D, null);
}


var earthColorMapTexture;
var earthSpecularMapTexture;
var textureImage="./textures/earth_cloudless.jpg";

function initTextures() {
	earthColorMapTexture = gl.createTexture();
	earthColorMapTexture.image = new Image();
	earthColorMapTexture.image.onload = function () {
		handleLoadedTexture(earthColorMapTexture)
	}
	earthColorMapTexture.image.src = textureImage;
}
function changeObject() {
	var id = document.getElementById("objectList").value;

	if(id==1) textureImage="./textures/mercury.jpg";
	else if(id==2) textureImage="./textures/venus.jpg";
	else if(id==3) textureImage="./textures/earth.jpg";
	else if(id==4) textureImage="./textures/earth_cloudless.jpg";
	else if(id==5) textureImage="./textures/moon.jpg";
	else if(id==6) textureImage="./textures/mars.jpg";
	else if(id==7) textureImage="./textures/jupiter.jpg";
	else if(id==8) textureImage="./textures/saturn.jpg";
	else if(id==9) textureImage="./textures/uranus.jpg";
	else if(id==10) textureImage="./textures/neptune.jpg";
	else if(id==11) textureImage="./textures/pluto.jpg";
	else return;

	moonRotationMatrix=null;
	moonRotationMatrix = mat4.create();
	mat4.identity(moonRotationMatrix);

	
	
	setOrbitalTilt();
	initTextures();	
}
function setOrbitalTilt() {
	var id = document.getElementById("objectList").value;

	if(id==1) orbitalTilt=0.01;
	else if(id==2) orbitalTilt=177.4;
	else if(id==3) orbitalTilt=23.4;
	else if(id==4) orbitalTilt=23.4;
	else if(id==5) orbitalTilt=6.7;
	else if(id==6) orbitalTilt=25.2;
	else if(id==7) orbitalTilt=3.1;
	else if(id==8) orbitalTilt=26.7;
	else if(id==9) orbitalTilt=97.8;
	else if(id==10) orbitalTilt=28.3;
	else if(id==11) orbitalTilt=122.5;
	else return;
}

var mvMatrix = mat4.create();
var mvMatrixStack = [];
var pMatrix = mat4.create();

function mvPushMatrix() {
	var copy = mat4.create();
	mat4.set(mvMatrix, copy);
	mvMatrixStack.push(copy);
}

function mvPopMatrix() {
	if (mvMatrixStack.length == 0) {
		throw "Invalid popMatrix!";
	}
	mvMatrix = mvMatrixStack.pop();
}

function setMatrixUniforms() {
	gl.uniformMatrix4fv(shaderProgram.pMatrixUniform, false, pMatrix);
	gl.uniformMatrix4fv(shaderProgram.mvMatrixUniform, false, mvMatrix);

	var normalMatrix = mat3.create();
	mat4.toInverseMat3(mvMatrix, normalMatrix);
	mat3.transpose(normalMatrix);
	gl.uniformMatrix3fv(shaderProgram.nMatrixUniform, false, normalMatrix);
}

function degToRad(degrees) {
	return degrees * Math.PI / 180;
}


var sphereVertexNormalBuffer;
var sphereVertexTextureCoordBuffer;
var sphereVertexPositionBuffer;
var sphereVertexIndexBuffer;

function initBuffers() {
	var latitudeBands = 60;
	var longitudeBands = 60;
	var radius = 13;

	var vertexPositionData = [];
	var normalData = [];
	var textureCoordData = [];
	for (var latNumber=0; latNumber <= latitudeBands; latNumber++) {
		var theta = latNumber * Math.PI / latitudeBands;
		var sinTheta = Math.sin(theta);
		var cosTheta = Math.cos(theta);

		for (var longNumber=0; longNumber <= longitudeBands; longNumber++) {
			var phi = longNumber * 2 * Math.PI / longitudeBands;
			var sinPhi = Math.sin(phi);
			var cosPhi = Math.cos(phi);

			var x = cosPhi * sinTheta;
			var y = cosTheta;
			var z = sinPhi * sinTheta;
			var u = 1 - (longNumber / longitudeBands);
			var v = 1 - (latNumber / latitudeBands);

			normalData.push(x);
			normalData.push(y);
			normalData.push(z);
			textureCoordData.push(u);
			textureCoordData.push(v);
			vertexPositionData.push(radius * x);
			vertexPositionData.push(radius * y);
			vertexPositionData.push(radius * z);
		}
	}

	var indexData = [];
	for (var latNumber=0; latNumber < latitudeBands; latNumber++) {
		for (var longNumber=0; longNumber < longitudeBands; longNumber++) {
			var first = (latNumber * (longitudeBands + 1)) + longNumber;
			var second = first + longitudeBands + 1;
			indexData.push(first);
			indexData.push(second);
			indexData.push(first + 1);

			indexData.push(second);
			indexData.push(second + 1);
			indexData.push(first + 1);
		}
	}

	sphereVertexNormalBuffer = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, sphereVertexNormalBuffer);
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(normalData), gl.STATIC_DRAW);
	sphereVertexNormalBuffer.itemSize = 3;
	sphereVertexNormalBuffer.numItems = normalData.length / 3;

	sphereVertexTextureCoordBuffer = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, sphereVertexTextureCoordBuffer);
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(textureCoordData), gl.STATIC_DRAW);
	sphereVertexTextureCoordBuffer.itemSize = 2;
	sphereVertexTextureCoordBuffer.numItems = textureCoordData.length / 2;

	sphereVertexPositionBuffer = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, sphereVertexPositionBuffer);
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(vertexPositionData), gl.STATIC_DRAW);
	sphereVertexPositionBuffer.itemSize = 3;
	sphereVertexPositionBuffer.numItems = vertexPositionData.length / 3;

	sphereVertexIndexBuffer = gl.createBuffer();
	gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, sphereVertexIndexBuffer);
	gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(indexData), gl.STREAM_DRAW);
	sphereVertexIndexBuffer.itemSize = 1;
	sphereVertexIndexBuffer.numItems = indexData.length;
}


var earthAngle = 180;
var lighting = true;
var angleONOFF = true;
function onofflight() {
	if(lighting==true) {
		lighting=false;
		$('#lightONOFF').html("<img src='icons/18237568211618698356.png' />");
	}
	else {
		lighting=true;
		$('#lightONOFF').html("<img src='icons/12805906211668004796.png' />");
	}
}

function onoffangle() {
	if(angleONOFF==true) {
		angleONOFF=false;
		orbitalTilt=0.0;
		$('#angleONOFF').html("<img src='icons/123456789876543234.png' />");
	}
	else {
		angleONOFF=true;
		setOrbitalTilt();
		$('#angleONOFF').html("<img src='icons/672082440498509814.png' />");
	}
}
var zoomLevel=-40;
var orbitalTilt=23.5;

function drawScene() {
	gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
	gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

	mat4.perspective(45, gl.viewportWidth / gl.viewportHeight, 0.1, 200.0, pMatrix);

	gl.uniform1i(shaderProgram.useColorMapUniform, true);

	gl.uniform1i(shaderProgram.useLightingUniform, lighting);
	if (lighting) {
		gl.uniform3f(shaderProgram.ambientColorUniform,0.4,0.4,0.4);
		gl.uniform3f(shaderProgram.pointLightingLocationUniform,-10.0,4.0,-20.0);
		gl.uniform3f(shaderProgram.pointLightingSpecularColorUniform,5.0,5.0,5.0);
		gl.uniform3f(shaderProgram.pointLightingDiffuseColorUniform,0.8,0.8,0.8);
	}

	mat4.identity(mvMatrix);

	mat4.translate(mvMatrix, [0, 0, zoomLevel]);
	mat4.multiply(mvMatrix, moonRotationMatrix);
	mat4.rotate(mvMatrix, degToRad(orbitalTilt), [1, 0, -1]);
	mat4.rotate(mvMatrix, degToRad(earthAngle), [0, 1, 0]);

	gl.activeTexture(gl.TEXTURE0);
	gl.bindTexture(gl.TEXTURE_2D, earthColorMapTexture);
	gl.uniform1i(shaderProgram.colorMapSamplerUniform, 0);

	gl.activeTexture(gl.TEXTURE1);
	gl.bindTexture(gl.TEXTURE_2D, earthSpecularMapTexture);
	gl.uniform1i(shaderProgram.specularMapSamplerUniform, 1);

	gl.bindBuffer(gl.ARRAY_BUFFER, sphereVertexPositionBuffer);
	gl.vertexAttribPointer(shaderProgram.vertexPositionAttribute, sphereVertexPositionBuffer.itemSize, gl.FLOAT, false, 0, 0);

	gl.bindBuffer(gl.ARRAY_BUFFER, sphereVertexTextureCoordBuffer);
	gl.vertexAttribPointer(shaderProgram.textureCoordAttribute, sphereVertexTextureCoordBuffer.itemSize, gl.FLOAT, false, 0, 0);

	gl.bindBuffer(gl.ARRAY_BUFFER, sphereVertexNormalBuffer);
	gl.vertexAttribPointer(shaderProgram.vertexNormalAttribute, sphereVertexNormalBuffer.itemSize, gl.FLOAT, false, 0, 0);

	gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, sphereVertexIndexBuffer);
	setMatrixUniforms();
	gl.drawElements(gl.TRIANGLES, sphereVertexIndexBuffer.numItems, gl.UNSIGNED_SHORT, 0);
}


var lastTime = 0;
var rotonoff=1;

function reboot() {
	moonRotationMatrix=null;
	moonRotationMatrix = mat4.create();
	mat4.identity(moonRotationMatrix);
	zoomLevel=-40;
	document.getElementById("zoomlevel").value=40;
}

function onoffrotate() {
	if(rotonoff==1) {
		rotonoff=0;
		$('#rotONOFF').html("<img src='icons/9162455922122652513.png' />");
	}
	else {
		rotonoff=1;
		$('#rotONOFF').html("<img src='icons/746847906690876932.png' />");
	}
}

function animate() {
	if(rotonoff==1) earthAngle += 0.7;
}
function setZoom() {
	zoomLevel = -1*document.getElementById("zoomlevel").value;
}
function tick() {
	requestAnimFrame(tick);
	drawScene();
	animate();
}

var mouseDown = false;
var lastMouseX = null;
var lastMouseY = null;

var moonRotationMatrix = mat4.create();
mat4.identity(moonRotationMatrix);

function handleMouseDown(event) {
	mouseDown = true;
	lastMouseX = event.clientX;
	lastMouseY = event.clientY;
}


function handleMouseUp(event) {
	mouseDown = false;
}


function handleMouseMove(event) {
	if (!mouseDown) {
		return;
	}
	var newX = event.clientX;
	var newY = event.clientY;

	var deltaX = newX - lastMouseX
	var newRotationMatrix = mat4.create();
	mat4.identity(newRotationMatrix);
	mat4.rotate(newRotationMatrix, degToRad(deltaX / 10), [0, 1, 0]);

	var deltaY = newY - lastMouseY;
	mat4.rotate(newRotationMatrix, degToRad(deltaY / 10), [1, 0, 0]);

	mat4.multiply(newRotationMatrix, moonRotationMatrix, moonRotationMatrix);

	lastMouseX = newX
	lastMouseY = newY;
}

function webGLStart() {	
	$('#frame').html("<canvas id='mainCanvas' style='border: none;' height='"+window.innerHeight+"' width='"+window.innerWidth+"'></canvas>");
			


	var canvas = document.getElementById("mainCanvas");
	initGL(canvas);
	initShaders();
	initBuffers();
	initTextures();
	
	gl.clearColor(0.0, 0.0, 0.0, 1.0);
	gl.enable(gl.DEPTH_TEST);
	
	
	canvas.onmousedown = handleMouseDown;
	document.onmouseup = handleMouseUp;
	document.onmousemove = handleMouseMove;
	
	tick();
}
</script>
<style>
@font-face {
font-family: nameFont;
src: url('./fonts/name.ttf');
}
*, body, html {
	margin: 0px;
	padding: 0px;
	background: #000;
	font-family: nameFont;
}
#name {
	position: absolute;
	background: rgba(0,0,0,0);
	top: 0px;
	left: 0px;
	z-index: 2;
	color: #CCC;	
	padding: 10px;
}
#controlPanel {
	position: absolute;
	left: 0px;
	bottom: 0px;
	right: 0px;
	height: 50px;
	padding: 5px;
	background: rgba(255,0,0,0.7);
	z-index: 2;
	background-image: url(./icons/11428525131342008626.png);
	background-position: 10px 15px;
	background-repeat: no-repeat;
}
#obListDiv, #rotONOFF, #lightONOFF, #angleONOFF, #zoom, #reboot, #infoONOFF {
	background: none;
	float: left;
}
#rotONOFF, #lightONOFF, #angleONOFF, #zoom, #infoONOFF, #reboot {
	background: #FFF;
	margin-left: 20px;
	margin-top: 9px;
	border-radius: 5px;
}
#zoomIn, #zoomOut, #zoomSlider {
	margin-left: 5px;
	margin-right: 5px;
	background: #FFF;
	float: left;	
}
#zoomSlider {
	padding-bottom: 5px;
}
#infoFrame {
	background: rgba(0,0,0,0);
	position: absolute;
	z-index: 2;
	left: 0px;
	bottom: 62px;
	width: 200px;
	height: 100px;
}
#infoBox {
	background:#666;
	padding: 10px;
	width: 180px;
	height: 80px;
}
img {
	background: none;
}
select {
	background: #FFF;
	padding: 10px;
	width: 200px;
	margin-left: 70px;
	margin-top: 5px;
}
option {
	background: #FFF;
	padding-right: 20px;
}
#frame {
	cursor: url(./icons/2650962781700503020.png);
}
#zoomSlider {
	transform: rotate(180deg);
-ms-transform: rotate(180deg); /* IE 9 */
-webkit-transform: rotate(180deg); /* Safari and Chrome */
-o-transform: rotate(180deg); /* Opera */
-moz-transform: rotate(180deg); /* Firefox */
}
</style>
</head>
<body onLoad="webGLStart();">
<div id='name'>Planetary Explorers</div>
<div id='frame'>
</div>
<div id='controlPanel'>
    <div id='obListDiv'>
        <select id='objectList' onChange="changeObject();">
            <option value="1">Mercury</option>
            <option value="2">Venus</option>
            <option value="3">Earth</option>
            <option selected="selected" value="4">Earth (cloudless)</option>
            <option value="5">Moon</option>
            <option value="6">Mars</option>
            <option value="7">Jupiter</option>
            <option value="8">Saturn</option>
            <option value="9">Uranus</option>
            <option value="10">Neptune</option>
            <option value="11">Pluto</option>
        </select>
    </div>
    <div id='rotONOFF' onClick="onoffrotate();"><img src="icons/746847906690876932.png" /></div>
    <div id='lightONOFF' onClick="onofflight();"><img src="icons/12805906211668004796.png" /></div>
    <div id='angleONOFF' onClick="onoffangle();"><img src="icons/672082440498509814.png" /></div>

    <div id='zoom'>
        <div id='zoomout'><img src="icons/836188492660525616.png" /></div>
        <div id='zoomslider'><input onChange='setZoom();' type='range' id='zoomlevel' min='15' max='150' value='40' /></div>
        <div id='zoomin'><img src='icons/3274527452000960463.png' /></div>
    </div>

    <div id='reboot' onClick="reboot();"><img src="icons/18621351541094580459.png" /></div>
	<div id='infoONOFF' onClick="$('#infoFrame').toggle();"><img src="icons/13676174261370205329.png" /></div>

</div>
<div id='infoFrame' onMouseOver="$('#infoBox').hide();" onMouseOut="$('#infoBox').fadeIn(200);">
	<div id='infoBox'>
    	Info Box<br /><br />
        <span style='background: none; color:#FFF; font-size: 12px; font-family: Georgia, Times, serif;'>Lighting : ON</span><br />
		<span style='background: none; color:#FFF; font-size: 12px; font-family: Georgia, Times, serif;'>Axial Tilt : ON</span>
    </div>
</div>
</body>
</html>
""")

app = webapp2.WSGIApplication([('/', MainHandler)],
                              debug=True)
