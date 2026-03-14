const menu = document.querySelector('#mobile-menu');
const menuLinks = document.querySelector('.navbar__menu');
const navLogo = document.querySelector('#navbar__logo');

// Display Mobile Menu
const mobileMenu = () => {
  menu.classList.toggle('is-active');
  menuLinks.classList.toggle('active');
};

menu.addEventListener('click', mobileMenu);

// // Show active menu when scrolling
// const highlightMenu = () => {
//   const elem = document.querySelector('.highlight');
//   const homeMenu = document.querySelector('#home-page');
//   const skillsMenu = document.querySelector('#skills-page');
//   const portfolioMenu = document.querySelector('#portfolio-page');
//   const experienceMenu = document.querySelector('#experience-page');
//   let scrollPos = window.scrollY;
//   // console.log(scrollPos);

//   // adds 'highlight' class to my menu items
//   if (window.innerWidth > 960 && scrollPos < 600) {
//     skillsMenu.classList.add('highlight');
//     // homeMenu.classList.remove('highlight');
//     return;
//   } else if (window.innerWidth > 1000 && scrollPos < 1400) {
//     skillsMenu.classList.add('highlight');
//     homeMenu.classList.remove('highlight');
//     portfolioMenu.classList.remove('highlight');
//     return;
//   } else if (window.innerWidth > 1400 && scrollPos < 1900) {
//     portfolioMenu.classList.add('highlight');
//     skillsMenu.classList.remove('highlight');
//     return;
//   }

//   if ((elem && window.innerWidth < 1900 && scrollPos < 600) || elem) {
//     elem.classList.remove('highlight');
//   }
// };

if (typeof highlightMenu === 'function') {
  window.addEventListener('scroll', highlightMenu);
  window.addEventListener('click', highlightMenu);
}

//  Close mobile Menu when clicking on a menu item
const hideMobileMenu = () => {
  const menuBars = document.querySelector('.is-active');
  if (window.innerWidth <= 768 && menuBars) {
    menu.classList.toggle('is-active');
    menuLinks.classList.remove('active');
  }
};

menuLinks.addEventListener('click', hideMobileMenu);
navLogo.addEventListener('click', hideMobileMenu);


//mix it up filter
if (typeof mixitup === 'function' && document.querySelector('.portfolio__container')) {
  mixitup('.portfolio__container', {
    selectors: {
      target: '.portfolio__content'
    },
    animation: {
      duration: 300
    }
  });
}

const linkPortfolio = document.querySelectorAll('.portfolio__item')

function activePortfolio(){
  if(linkPortfolio){

    linkPortfolio.forEach(l => l.classList.remove('active-portfolio'))
    this.classList.add('active-portfolio')
  }
}
linkPortfolio.forEach(l => l.addEventListener('click', activePortfolio))

// #f9f9f9, #8cada7, #a5d0a8);
//ctx.fillStyle = "white";
//ctx.font = "30px Arial"
//ctx.fillText("welcome", 100, 100);

//canvas.setAttribute("aria-label", "welcome");
