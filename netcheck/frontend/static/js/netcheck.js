const bgp_info = '<label>Expected # of BGP Routes</label> <input id="testParam" name="bgp_routes" type="number" /><br><label>Expected # of BGP Neighbors</label> <input id="testParam" name="bgp_neighbors" type="number" />';

const env_info = '<label>CPU Utilization (%)</label> <input id="testParam" name="cpu_util" type="number" /><br><label>Memory Utilization (%)</label> <input id="testParam" name="mem_util" type="number" />';

const ospf_info = '<label>Expected # of OSPF Routes</label> <input id="testParam" name="ospf_routes" type="number" /><br><label>Expected # of OSPF Neighbors</label> <input id="testParam" name="ospf_neighbors" type="number" />';

const no_data = '<label>No Data</label>'

$(document).ready(function () {
	$('.drag').draggable({
		appendTo: 'body',
		helper: 'clone'
	});
	
	$('#dropzone').droppable({
		activeClass: 'active',
		hoverClass: 'hover',
		accept: ":not(.ui-sortable-helper)", // Reject clones generated by sortable
		
		drop: function (e, ui) {
			// add test to list
			if (ui.draggable.text().includes("BGP")) {
				var $el = $('<div class="drop-item"><testcase>' + ui.draggable.text() + '</testcase><div><details>' + bgp_info + '</div></details></div>');
			} else if (ui.draggable.text().includes("Environment")) {
				var $el = $('<div class="drop-item"><testcase>' + ui.draggable.text() + '</testcase><div><details>' + env_info + '</div></details></div>');
			} else if (ui.draggable.text().includes("OSPF")) {
				var $el = $('<div class="drop-item"><testcase>' + ui.draggable.text() + '</testcase><div><details>' + ospf_info + '</div></details></div>');
			} else {
				var $el = $('<div class="drop-item"><testcase>' + ui.draggable.text() + '</testcase><div><details>' + no_data + '</div></details></div>');
			}

			
			// add trash can to remove test from list
			$el.append($('<button type="button" class="btn btn-default btn-xs remove"><span class="bi bi-trash"></span></button>').click(function () { $(this).parent().detach(); }));
			$(this).append($el);
		}
	}).sortable({
		items: '.drop-item',
		sort: function () {
			// gets added unintentionally by droppable interacting with sortable
			// using connectWithSortable fixes this, but doesn't allow you to customize active/hoverClass options
			$(this).removeClass("active");
		}
	});

	$("#custom_validation_form").submit(function () {

		var value = $("#dropzone").html();
		console.log(value)
	});

	(() => {
		'use strict';
	  
		// Fetch all the forms we want to apply custom Bootstrap validation styles to
		const forms = document.querySelectorAll('.needs-validation');
	  
		// Loop over them and prevent submission
		Array.prototype.slice.call(forms).forEach((form) => {
		  form.addEventListener('submit', (event) => {
			if (!form.checkValidity()) {
			  event.preventDefault();
			  event.stopPropagation();
			}
			form.classList.add('was-validated');
		  }, false);
		});
	  })();

});

function saveTextAsFile(textToWrite, fileNameToSaveAs) {
	var textFileAsBlob = new Blob([textToWrite], { type: 'text/plain' });
	var downloadLink = document.createElement("a");
	downloadLink.download = fileNameToSaveAs;
	downloadLink.innerHTML = "Download File";
	if (window.webkitURL != null) {
		// Chrome allows the link to be clicked
		// without actually adding it to the DOM.
		downloadLink.href = window.webkitURL.createObjectURL(textFileAsBlob);
	}
	else {
		// Firefox requires the link to be added to the DOM
		// before it can be clicked.
		downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
		downloadLink.onclick = destroyClickedElement;
		downloadLink.style.display = "none";
		document.body.appendChild(downloadLink);
	}

	downloadLink.click();
}

function sendTestDetails() {
	// const drops = document.getElementById("dropzone").innerHTML
	const user_test_name = document.getElementById("testName").value;
	const testcase_names = document.querySelectorAll("testcase");
	const test_details = document.querySelectorAll('input');
	const test_names = [];
	const test_params = [];

	// loop through inputs and only capture test params and values
	for (let i = 0; i < testcase_names.length; i++) {
		test_names.push(testcase_names[i].textContent)
	}
	
	for (let i = 0; i < test_details.length; i++) {
		if (test_details[i].id == "testParam") {
			var param_name = test_details[i].name
			var param_val = test_details[i].value
			const dict = {
				param_name: param_name,
				param_value: param_val
			}
			test_params.push(dict)
			// test_params.push(test_details[i].name)
			// test_params.push(test_details[i].value)
		}
	}
	console.log(test_names)
	console.log(test_params)

	var xhr = new XMLHttpRequest();
	xhr.open("POST", "/custom-post", true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	xhr.send(JSON.stringify({
		"test_name": user_test_name,
		"tests": test_names,
		"test_details": test_params
	}));
}
