window.onload = () => {
  let captcha = document.querySelector(`#captcha-text`)
  captcha.placeholder = `Enter the captcha`

  let image = document.querySelector(`#image`)

  image.addEventListener(`click`, (event) => {
    window.scrollTo(0, document.body.scrollHeight)
  })
}

function validate() {
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
    let file = file.files[0]

    if (file.size > max_size) {
      return false
    }
  }

  return true
}