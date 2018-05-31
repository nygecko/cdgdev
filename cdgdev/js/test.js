
function goBack() {
history.back();
}

function checkChanges() {

var fieldNames = ['field0', 'field1', 'field2', 'field3', 'field4', 'field5', 'field6', 'field7', 'field8', 'field9', 'field10', 'field11']; 
	
// check to make sure datalist field5 only uses valid datalist values
if (document.getElementById('field5').value)
{
	var buOptions = document.getElementById('bizunittype').options;
	var buOptionOk = false;

	for (var j=0; j<buOptions.length; j++)
	{
		if (document.getElementById('field5').value == buOptions[j].value) 
		{
			buOptionOk = true;
			break;
		}
	}

	if (!buOptionOk)
	{
		document.getElementById('field5').value = '';
		alert('BizUnit field is not valid');
		// set back to previous value
		document.getElementById('field5').value = document.getElementById(fieldNames[5]).placeholder;
	}
}

// check to make sure datalist field7 only uses valid datalist values
if (document.getElementById('field7').value)
{

	var statOptions = document.getElementById('statustype').options;
	var statOptionOk = false;

	for (var k=0; k<statOptions.length; k++)
	{
		if (document.getElementById('field7').value == statOptions[k].value) 
		{
			statOptionOk = true;
			break;
		}
	}

	if (!statOptionOk)
	{
		document.getElementById('field7').value = '';
		alert('Status field is not valid');
		// set back to previous value
		document.getElementById('field7').value = document.getElementById(fieldNames[7]).placeholder;
	}
}


// highlight changed fields
for (i=0; i<fieldNames.length; i++)
{
	newVal = document.getElementById(fieldNames[i]).value;
	origVal = document.getElementById(fieldNames[i]).placeholder;

	if (newVal != origVal)
	{
		document.getElementById(fieldNames[i]).style.color = 'red';
	}
}

document.updateForm.submit();
}
