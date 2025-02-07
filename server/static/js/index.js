let clicked = false

window.onload = () => {
  let captcha = document.querySelector(`#captcha-text`)

  if (captcha) {
    captcha.placeholder = `Enter the captcha`
  }

  let image = document.querySelector(`#image`)

  if (image) {
    image.addEventListener(`click`, (event) => {
      window.scrollTo(0, document.body.scrollHeight)
    })
  }
}

function validate() {
  if (clicked) {
    return false
  }

  let captcha = document.querySelector(`#captcha-text`)

  if (captcha) {
    if (!captcha.value.trim()) {
      return false
    }
  }

  let key = document.querySelector(`#key`)

  if (key) {
    if (!key.value.trim()) {
      return false
    }
  }

  let file = document.querySelector(`#file`)

  if (file.files.length > 0) {
    if (file.files[0].size > max_size) {
      return false
    }
  }

  clicked = true
  return true
}