function singplural(what, length) {
  if (length === 1) {
    return what
  }

  return `${what}s`
}

function shuffle_array(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]]
  }

  return array
}

async function copy_to_clipboard(text) {
  navigator.clipboard.writeText(text)
}

function select_all(el) {
  let selection = window.getSelection()
  let range = document.createRange()
  range.selectNodeContents(el)
  selection.removeAllRanges()
  selection.addRange(range)
}

function is_image(file) {
  return file.type.match(`image/*`)
}

function is_audio(file) {
  return file.type.match(`audio/*`)
}

function is_video(file) {
  return file.type.match(`video/*`)
}

function set_css_var(name, value) {
  document.documentElement.style.setProperty(`--${name}`, value)
}

function print_error(msg) {
  // eslint-disable-next-line no-console
  console.log(`Error: ${msg}`)
}