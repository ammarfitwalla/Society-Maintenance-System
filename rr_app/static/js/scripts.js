/* Description: Custom JS file */

/* Navigation*/
// Collapse the navbar by adding the top-nav-collapse class
window.onscroll = function () {
  scrollFunction();
  scrollFunctionBTT(); // back to top button
};

window.onload = function () {
  scrollFunction();
};

function scrollFunction() {
  if (document.documentElement.scrollTop > 30) {
    document.getElementById("navbar").classList.add("top-nav-collapse");
  } else if (document.documentElement.scrollTop < 30) {
    document.getElementById("navbar").classList.remove("top-nav-collapse");
  }
}

// Navbar on mobile
let elements = document.querySelectorAll(".nav-link:not(.dropdown-toggle)");

for (let i = 0; i < elements.length; i++) {
  elements[i].addEventListener("click", () => {
    document.querySelector(".offcanvas-collapse").classList.toggle("open");
  });
}

document.querySelector(".navbar-toggler").addEventListener("click", () => {
  document.querySelector(".offcanvas-collapse").classList.toggle("open");
});

// Hover on desktop
function toggleDropdown(e) {
  const _d = e.target.closest(".dropdown");
  let _m = document.querySelector(".dropdown-menu", _d);

  setTimeout(
    function () {
      const shouldOpen = _d.matches(":hover");
      _m.classList.toggle("show", shouldOpen);
      _d.classList.toggle("show", shouldOpen);

      _d.setAttribute("aria-expanded", shouldOpen);
    },
    e.type === "mouseleave" ? 300 : 0
  );
}

// On hover
const dropdownCheck = document.querySelector('.dropdown');

if (dropdownCheck !== null) {
  document.querySelector(".dropdown").addEventListener("mouseleave", toggleDropdown);
  document.querySelector(".dropdown").addEventListener("mouseover", toggleDropdown);

  // On click
  document.querySelector(".dropdown").addEventListener("click", (e) => {
    const _d = e.target.closest(".dropdown");
    let _m = document.querySelector(".dropdown-menu", _d);
    if (_d.classList.contains("show")) {
      _m.classList.remove("show");
      _d.classList.remove("show");
    } else {
      _m.classList.add("show");
      _d.classList.add("show");
    }
  });
}


/* Card Slider - Swiper */
var cardSlider = new Swiper('.card-slider', {
  autoplay: {
    delay: 4000,
    disableOnInteraction: false
  },
  loop: true,
  navigation: {
    nextEl: '.swiper-button-next',
    prevEl: '.swiper-button-prev'
  }
});


/* Back To Top Button */
// Get the button
myButton = document.getElementById("myBtn");

// When the user scrolls down 20px from the top of the document, show the button
function scrollFunctionBTT() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    myButton.style.display = "block";
  } else {
    myButton.style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  document.body.scrollTop = 0; // for Safari
  document.documentElement.scrollTop = 0; // for Chrome, Firefox, IE and Opera
}

function readOnly(elemtName) {
  let elem = document.getElementById(elemtName);
  elem.setAttribute("readonly", "readonly");
}

function hideShowDiv(elementName, hideShow) {
  let element = document.getElementById(elementName);
  if (hideShow == "Show") {
    element.removeAttribute("hidden");
  } else {
    element.setAttribute("hidden", "hidden");
  }

}

function formValidityCheck(formName) {
  var Form = document.getElementById(formName);
  if (Form.checkValidity() == false) {
    var list = Form.querySelectorAll(':invalid');
    for (var item of list) {
      item.focus();
      // console.log(item)
      // console.log(item.id)
      var label_ = Form.querySelector('label[for=' + item.id + ']');
      // console.log(label_)

      Swal.fire(item.validationMessage, label_.textContent, 'info')
      return false
    }
  } return Form
}

function confirmAction() {
  Form = formValidityCheck('masterForm')
  if (Form) {
    let t_name = document.getElementById("tenant_id").value
    var edit_ele = document.getElementById("divUpdate")
    let edit_ele_hide = window.getComputedStyle(edit_ele).display
    // console.log('edit_ele_hide', edit_ele_hide)
    
    Swal.fire({
      title: edit_ele_hide == 'none' ? "Add New Tenant" : "Update Tenant",
      text: edit_ele_hide == 'none' ? "Are you sure you want to Add new Tenant '" + t_name + "' ?" : "Are you sure you want to Update Tenant '" + t_name + "' ?",
      icon: 'question',
      showDenyButton: true,
      confirmButtonText: 'Yes',
      denyButtonText: `No`,
    }).then((result) => {
      if (result.isConfirmed) {
        Form.submit()
        console.log('check_submitcheck_submit')
      } else if (result.isDenied) {
        Swal.fire(edit_ele_hide == 'none' ? 'New Tenant Add operation is cancelled!' : 'Update Tenant operation is cancelled!', '', 'error')
      }
    })
  }
}

function monthDiff() {
  var d_from = document.getElementById("from_date").value;
  var d_to = document.getElementById("to_date").value;

  if (d_from && d_to) {

    if (parseInt(d_to.split('-')[0]) != parseInt(d_from.split('-')[0])) {
      var y_diff = parseInt(d_to.split('-')[0]) - parseInt(d_from.split('-')[0]);
    } else {
      var y_diff = 0
    }

    var m_diff = parseInt(d_to.split('-')[1]) - parseInt(d_from.split('-')[1])
    // document.getElementById("tm").value = m_diff;
    document.getElementById("tm").value = m_diff + (12 * y_diff) + 1;
    multiplyMonth();
  }
}

function multiplyMonth() {
  var rate = document.getElementById("rate").value;
  var tm = document.getElementById("tm").value;
  if (rate && tm) {
    var t_rupees = rate * tm
    if (isNaN(t_rupees)) {
      document.getElementById("tr").value = 0;
    } else {
      document.getElementById("tr").value = t_rupees;
    }
  }
}

function printAction() {
  Form = formValidityCheck('billForm')
  if (Form) {
    let bill_num = document.getElementById("bill_number").value

    Swal.fire({
      title: "Print Bill",
      text: "Are you sure you want to Print Bill '" + bill_num + "' ?",
      icon: 'question',
      showDenyButton: true,
      confirmButtonText: 'Yes',
      denyButtonText: `No`,
    }).then((result) => {
      if (result.isConfirmed) {
        console.log('PrintBillPrintBill')
        document.getElementById("printId").value = "Print";
        Form.submit()
      } else if (result.isDenied) {
        document.getElementById("printId").value = "";
        Swal.fire('Print Bill operation is cancelled!', '', 'error')
      }
    })
  }
}

function confirmBillAction() {
  Form = formValidityCheck('billForm')
  if (Form) {
    let bill_num = document.getElementById("bill_number").value
    var edit_ele = document.getElementById("divUpdate")
    let edit_ele_hide = window.getComputedStyle(edit_ele).display
    // console.log('edit_ele_hide', edit_ele_hide)
    
    Swal.fire({
      title: edit_ele_hide == 'none' ? "Add New Bill" : "Update Bill",
      text: edit_ele_hide == 'none' ? "Are you sure you want to Add new Bill '" + bill_num + "' ?" : "Are you sure you want to Update Bill '" + bill_num + "' ?",
      icon: 'question',
      showDenyButton: true,
      confirmButtonText: 'Yes',
      denyButtonText: `No`,
    }).then((result) => {
      if (result.isConfirmed) {
        console.log('check_submitcheck_submit')
        Form.submit()
      } else if (result.isDenied) {
        Swal.fire(edit_ele_hide == 'none' ? 'New Bill Add operation is cancelled!' : 'Update Bill operation is cancelled!', '', 'error')
      }
    })
  }
}