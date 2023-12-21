window.onload = function () {
  // Store config from URL search params to local storage
  const searchParams = new URLSearchParams(window.location.search);
  if (searchParams.has("type")) {
    const type = searchParams.get("type");

    for (const [key, value] of searchParams.entries()) {
      if (key != "type") {
        const id = type + "-" + key;
        localStorage.setItem(id, value);
      }
    }
  }

  // Fill in form values from local storage
  for (const [key, value] of Object.entries(localStorage)) {
    if (document.getElementById(key)) {
      document.getElementById(key).value = value;
    }
  }
};
