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

function contains_url(text) {
  return text.match(/(https?:\/\/|www\.)\S+/gi)
}

function prompt_text(placeholder, callback, max = 0) {
  let msg = Msg.factory({
    persistent: false,
    disable_content_padding: true,
  })

  let c = DOM.create(`div`)
  c.id = `prompt_container`
  let input = DOM.create(`input`)
  input.id = `prompt_input`
  input.type = `text`
  input.placeholder = placeholder
  c.appendChild(input)
  msg.set(c)

  function submit() {
    callback(input.value)
    msg.close()
  }

  DOM.ev(input, `keydown`, (e) => {
    if (max > 0) {
      if (input.value.length > max) {
        input.value = input.value.substring(0, max).trim()
        return
      }
    }

    if (e.key === `Enter`) {
      submit()
      e.preventDefault()
    }
  })

  msg.show()
  input.focus()
}

function popmsg(message, callback) {
  let msg = Msg.factory({
    persistent: false,
    after_close: callback,
  })

  msg.show(message)
}