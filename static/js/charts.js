const pie = document.getElementById("pieChart");

new Chart(pie,{

    type:"pie",

    data:{

        labels:["Completed","Pending"],

        datasets:[{

            data:[completed,pending]

        }]

    }

});

const bar=document.getElementById("barChart");

new Chart(bar,{

    type:"bar",

    data:{

        labels:chartLabels,

        datasets:[{

            label:"Annotations",

            data:chartValues

        }]

    },

    options:{

        responsive:true,

        maintainAspectRatio:false

    }

});