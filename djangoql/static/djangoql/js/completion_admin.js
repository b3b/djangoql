(function (DjangoQL, showRelatedObjectPopup) {
  'use strict';

  function saveQueryPopup(e) {
    // Open Query object creation page, using Django admin popup functionality
    e.preventDefault();
    this.id = 'djangoql-save-query';
    this.href = 'save-djangoql-query/?text=' +
      encodeURIComponent(DjangoQL.textarea.value);
    showRelatedObjectPopup(this);
  }

  function createDropdownMenu() {
    var container = document.querySelector('.djangoql-save-icon-container');
    var dropdown = document.createElement('div');

    dropdown.className = 'djangoql-save-dropdown';
    dropdown.appendChild(createDropdownItem(
      'Show saved queries',
      '\u2605', // star symbol as an icon
      DjangoQL.switchSavedQueriesMode.bind(DjangoQL)
    ));
    dropdown.appendChild(createDropdownItem(
      'Save query',
      '\u2795', // bold Plus symbol as an icon
      saveQueryPopup
    ));
    container.appendChild(dropdown);
    return dropdown;
  }

  function createDropdownItem(label, icon, action) {
    var item = document.createElement('a');
    item.innerHTML = label;
    item.className = 'djangoql-save-dropdown-item';
    if (icon) {
      item.setAttribute('data-content', icon);
    }
    if (action !== undefined) {
      item.addEventListener('click', action);
    }
    return item;
  };

  DjangoQL.DOMReady(function () {
    // Replace standard search input with textarea
    var textarea;
    var input = document.querySelector('input[name=q]');
    if (!input) {
      return;
    }
    textarea = document.createElement('textarea');
    textarea.value = input.value;
    textarea.id = input.id;
    textarea.name = input.name;
    textarea.rows = 1;
    textarea.setAttribute('maxlength', 2000);
    input.parentNode.insertBefore(textarea, input);
    input.parentNode.removeChild(input);
    textarea.focus();

    DjangoQL.init({
      introspections: 'introspect/',
      syntaxHelp: 'djangoql-syntax/',
      savedQueriesIcon: true,
      selector: 'textarea[name=q]',
      autoResize: true
    });

    createDropdownMenu();
  });
}(window.DjangoQL, window.showRelatedObjectPopup));
