App.fade_delay = 100
App.audio_context = null
App.pitch_node = null
App.reverb_node = null
App.reverb_enabled = false
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
  }
}

App.video_faster = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.playbackRate = Math.min(10, video.playbackRate + 0.1)
  }
}

App.video_speed_reset = () => {
  let video = DOM.el(`#video`)

  if (video) {
    video.playbackRate = 1.0
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
      return false
    }
  }

  if (App.audio_context.state === `suspended`) {
    App.audio_context.resume()
  }

  if (!App.pitch_node || (video.audioSource !== App.current_audio_source)) {
    try {
      if (App.current_audio_source) {
        App.current_audio_source.disconnect()
      }

      let source = App.audio_context.createMediaElementSource(video)
      App.current_audio_source = source
      App.pitch_node = App.audio_context.createGain()

      // Create reverb node if not exists
      if (!App.reverb_node) {
        App.create_reverb_node()
      }

      // Connect audio chain: source -> pitch -> reverb -> destination
      source.connect(App.pitch_node)
      App.pitch_node.connect(App.reverb_node.input)
      App.reverb_node.output.connect(App.audio_context.destination)
      video.audioSource = source
    }
    catch (e) {
      if (e.name === `InvalidStateError`) {
        return true
      }

      return false
    }
  }

  return true
}

App.apply_pitch = (video) => {
  if (!video) {
    return
  }

  App.set_video_preserve_pitch(false)
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
  }
}

App.video_pitch_up = () => {
  let video = DOM.el(`#video`)

  if (video) {
    App.setup_audio_context(video)
    App.current_pitch_step = Math.min(12, App.current_pitch_step + App.pitch_step_size)
    App.apply_pitch(video)
  }
}

App.video_pitch_reset = () => {
  let video = DOM.el(`#video`)

  if (video) {
    App.set_video_preserve_pitch(true)
    App.current_pitch_step = 0
    video.playbackRate = 1.0
  }
}

App.set_video_preserve_pitch = (value) => {
  let video = DOM.el(`#video`)

  if (video) {
    try {
      if (`preservesPitch` in video) {
        video.preservesPitch = value
      }

      if (`mozPreservesPitch` in video) {
        video.mozPreservesPitch = value
      }

      if (`webkitPreservesPitch` in video) {
        video.webkitPreservesPitch = value
      }
    }
    catch (e) {
      App.print_error(`Could not set pitch flag:`, e)
    }
  }
}

App.create_reverb_node = () => {
  if (!App.audio_context) {
    return
  }

  try {
    let convolver = App.audio_context.createConvolver()
    let dry_gain = App.audio_context.createGain()
    let wet_gain = App.audio_context.createGain()
    let output_gain = App.audio_context.createGain()

    App.create_impulse_response(convolver)

    dry_gain.gain.value = 0.8
    wet_gain.gain.value = 0.0
    output_gain.gain.value = 1.0

    App.reverb_node = {
      input: App.audio_context.createGain(),
      convolver: convolver,
      dry: dry_gain,
      wet: wet_gain,
      output: output_gain,
    }

    App.reverb_node.input.connect(App.reverb_node.dry)
    App.reverb_node.input.connect(App.reverb_node.convolver)
    App.reverb_node.convolver.connect(App.reverb_node.wet)
    App.reverb_node.dry.connect(App.reverb_node.output)
    App.reverb_node.wet.connect(App.reverb_node.output)
  }
  catch (e) {
    App.print_error(`Could not create reverb node:`, e)
  }
}

App.create_impulse_response = (convolver) => {
  try {
    let sample_rate = App.audio_context.sampleRate
    let length = sample_rate * 2
    let impulse = App.audio_context.createBuffer(2, length, sample_rate)

    for (let channel = 0; channel < 2; channel++) {
      let channel_data = impulse.getChannelData(channel)

      for (let i = 0; i < length; i++) {
        let decay = Math.pow(1 - i / length, 2)
        let noise = (Math.random() * 2 - 1) * decay * 0.5
        channel_data[i] = noise
      }
    }

    convolver.buffer = impulse
  }
  catch (e) {
    App.print_error(`Could not create impulse response:`, e)
  }
}

App.video_reverb_on = () => {
  let video = DOM.el(`#video`)

  if (video) {
    if (!App.setup_audio_context(video)) {
      return
    }

    if (App.reverb_node) {
      App.reverb_enabled = true
      App.reverb_node.wet.gain.setValueAtTime(0.4, App.audio_context.currentTime)
      App.reverb_node.dry.gain.setValueAtTime(0.6, App.audio_context.currentTime)
    }
  }
}

App.video_reverb_off = () => {
  let video = DOM.el(`#video`)

  if (video) {
    if (App.reverb_node) {
      App.reverb_enabled = false
      App.reverb_node.wet.gain.setValueAtTime(0.0, App.audio_context.currentTime)
      App.reverb_node.dry.gain.setValueAtTime(0.8, App.audio_context.currentTime)
    }
  }
}

App.video_reverb_toggle = () => {
  let item = DOM.el(`#video_commands_opts_reverb`)

  if (App.reverb_enabled) {
    App.video_reverb_off()

    if (item) {
      item.classList.remove(`button_highlight`)
    }
  }
  else {
    App.video_reverb_on()
    let icon = App.icon(`enabled`)

    if (item) {
      item.classList.add(`button_highlight`)
    }
  }
}