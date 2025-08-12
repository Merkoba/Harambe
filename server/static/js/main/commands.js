App.fade_delay = 100
App.audio_context = null
App.pitch_node = null
App.current_pitch_step = 0
App.pitch_step_size = 1
App.current_audio_source = null

App.show_video_commands = () => {
  if ((App.mode === `post`) && DOM.el(`#video`)) {
    App.setup_video_commands_opts(true)
  }
}

App.video_jump = () => {
  let video = DOM.el(`#video`)

  if (video) {
    if (video.paused) {
      App.video_jump_enabled = true
      video.play()
    }
    else {
      App.video_jump_action()
    }
  }
}

App.video_jump_action = () => {
  App.video_jump_enabled = false
  let video = DOM.el(`#video`)

  if (video) {
    let duration = video.duration

    if (duration > 0) {
      let random_time = Math.random() * duration
      video.currentTime = random_time
    }
  }
}

App.video_rewind = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.currentTime = 0
    video.play()
  }
}

App.video_slower = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.playbackRate = Math.max(0.1, video.playbackRate - 0.1)
    video.play()
  }
}

App.video_faster = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.playbackRate = Math.min(10, video.playbackRate + 0.1)
    video.play()
  }
}

App.video_speed_reset = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.playbackRate = 1.0
    video.play()
  }
}

App.video_fade_in = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.volume = 0
    video.play()

    let fadeIn = setInterval(() => {
      if (video.volume < 1) {
        video.volume = Math.min(1, video.volume + 0.02)
      }
      else {
        clearInterval(fadeIn)
      }
    }, App.fade_delay)
  }
}

App.video_fade_out = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.volume = 1

    let fadeOut = setInterval(() => {
      if (video.volume > 0) {
        video.volume = Math.max(0, video.volume - 0.02)
      }
      else {
        clearInterval(fadeOut)
        video.pause()
      }
    }, App.fade_delay)
  }
}

App.setup_audio_context = (video) => {
  if (!App.audio_context) {
    try {
      App.audio_context = new (window.AudioContext || window.webkitAudioContext)()
    }
    catch (e) {
      console.error('Web Audio API not supported:', e)
      return false
    }
  }

  if (App.audio_context.state === 'suspended') {
    App.audio_context.resume()
  }

  if (!App.pitch_node || video.audioSource !== App.current_audio_source) {
    try {
      if (App.current_audio_source) {
        App.current_audio_source.disconnect()
      }

      let source = App.audio_context.createMediaElementSource(video)
      App.current_audio_source = source
      App.pitch_node = App.audio_context.createGain()
      source.connect(App.pitch_node)
      App.pitch_node.connect(App.audio_context.destination)
      video.audioSource = source
    }
    catch (e) {
      if (e.name === 'InvalidStateError') {
        console.warn('Audio source already connected, using existing setup')
        return true
      }

      console.error('Audio context setup error:', e)
      return false
    }
  }

  return true
}

App.apply_pitch = (video) => {
  if (!video) {
    return
  }

  try {
    if (`preservesPitch` in video) {
      video.preservesPitch = false
    }

    if (`mozPreservesPitch` in video) {
      video.mozPreservesPitch = false
    }

    if (`webkitPreservesPitch` in video) {
      video.webkitPreservesPitch = false
    }
  }
  catch (e) {
    console.warn('Could not set preservesPitch flag:', e)
  }

  let pitch_multi = Math.pow(2, App.current_pitch_step / 12)
  let new_rate = Math.max(0.25, Math.min(4.0, pitch_multi))
  video.playbackRate = new_rate
}

App.video_pitch_down = () => {
  let video = DOM.el(`#video`)

  if (video) {
    App.setup_audio_context(video)
    App.current_pitch_step = Math.max(-12, App.current_pitch_step - App.pitch_step_size)
    App.apply_pitch(video)

    if (video.paused) {
      video.play()
    }
  }
}

App.video_pitch_up = () => {
  let video = DOM.el(`#video`)

  if (video) {
    App.setup_audio_context(video)
    App.current_pitch_step = Math.min(12, App.current_pitch_step + App.pitch_step_size)
    App.apply_pitch(video)

    if (video.paused) {
      video.play()
    }
  }
}

App.video_pitch_reset = () => {
  let video = DOM.el(`#video`)

  if (video) {
    App.current_pitch_step = 0
    App.apply_pitch(video)
  }
}