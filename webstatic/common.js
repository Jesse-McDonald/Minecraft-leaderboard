
// Function to get the value of a cookie
function getCookie(cookieName) {
	const cookies = document.cookie.split('; ');
	for (const cookie of cookies) {
		const [name, value] = cookie.split('=');
		if (name === cookieName) {
			return value;
		}
	}
	return null;
}

function setCookie(cookieName, value) {
	document.cookie = `${cookieName}=${value}`;
	
}

const initialDarkCookie=localStorage.getItem('darkmode')
if(initialDarkCookie=='sane'){
		activateLightMode();
		document.getElementById('saneMode').checked=true;
	}else if(initialDarkCookie=='dark'){
		activateDarkMode();
		document.getElementById('darkMode').checked=true;
	}else if(initialDarkCookie=='amoled'){
		activateAmoledMode();
		document.getElementById('amoledMode').checked=true;
	}
function activateLightMode(){
	const rootElement = document.documentElement;
	rootElement.classList.remove('amoledmode');
	rootElement.classList.remove('darkmode');
	localStorage.setItem('darkmode','sane');
}

function activateDarkMode(){
	const rootElement = document.documentElement;
	rootElement.classList.remove('amoledmode');
	rootElement.classList.add('darkmode');
	localStorage.setItem('darkmode','dark')
}

function activateAmoledMode(){
		const rootElement = document.documentElement;
	rootElement.classList.remove('darkmode');
	rootElement.classList.add('amoledmode');
	localStorage.setItem('darkmode','amoled')
}



const initialUnitCookie=localStorage.getItem('raworunit')
document.getElementById("unitselector").checked=initialUnitCookie
toggleUnits()
function toggleUnits(){
	const rootElement = document.documentElement;
	const checked = document.getElementById("unitselector").checked
	if(checked){
		rootElement.classList.remove('useRaw');
		rootElement.classList.add('useUnit');
	}else{
		rootElement.classList.remove('useUnit');
		rootElement.classList.add('useRaw');
		
	}
	localStorage.setItem('raworunit',checked)
	
}