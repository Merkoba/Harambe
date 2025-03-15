#!/usr/bin/env ruby

require "optparse"
require "net/http"
require "uri"
require "json"
require "open3"

# Default values
url = "https://someurl.com"
username = "someusername"
password = "somepassword"
endpoint = "apiupload"

# Arguments
prompt = false
zip = "off"
privacy = "public"
file_path = nil
image_magic = "off"
audio_magic = "off"
audio_image_magic = "off"

# Parse command-line options
OptionParser.new do |opts|
  opts.banner = "Usage: upload.rb [options] <file_path>"

  opts.on("--prompt", "Prompt for the title") do
    prompt = true
  end

  opts.on("--zip", "Compress the file into a zip") do
    zip = "on"
  end

  opts.on("--private", "Make the post private") do
    privacy = "private"
  end

  opts.on("--image-magic", "Do image magic") do
    image_magic = "on"
  end

  opts.on("--audio-magic", "Do audio magic") do
    audio_magic = "on"
  end

  opts.on("--audio-image-magic", "Do audio magic") do
    audio_image_magic = "on"
  end

  opts.on("-h", "--help", "Prints this help") do
    puts opts
    exit
  end
end.parse!(into: {})

file_path = ARGV[0]

# Remove "file://" prefix if present
file_path = file_path.sub(/^file:\/\//, "") if file_path

# Convert to absolute path
file_path = File.absolute_path(file_path) if file_path

# Check required parameters
abort("Error: URL is not set") if url.nil? || url.empty?
abort("Error: USERNAME is not set") if username.nil? || username.empty?
abort("Error: PASSWORD is not set") if password.nil? || password.empty?
abort("Error: FILE_PATH is not set") if file_path.nil? || file_path.empty?

# Prompt to get the title
title = ""

if prompt
  filename = File.basename(file_path, ".*")
  title = `zenity --entry --title="Harambe Upload" --text="Enter a title:" --entry-text="#{filename}"`.chomp

  if $?.exitstatus != 0
    puts "User cancelled the input."
    exit 1
  end
end

puts "Uploading: #{file_path}"

# Make the POST request and capture the response
uri = URI("#{url}/#{endpoint}")
request = Net::HTTP::Post.new(uri)

form_data = [
  ["file", File.open(file_path)],
  ["title", title],
  ["username", username],
  ["password", password],
  ["zip", zip],
  ["privacy", privacy],
  ["image_magic", image_magic],
  ["audio_magic", audio_magic],
  ["audio_image_magic", audio_image_magic],
]

request.set_form form_data, "multipart/form-data"

response = Net::HTTP.start(uri.hostname, uri.port, use_ssl: uri.scheme == "https") do |http|
  http.request(request)
end

response_body = response.body

# Check if the response starts with "post/"
if response_body.start_with?("post/")
  full_url = "#{url}/#{response_body}"
  IO.popen(["xclip", "-selection", "clipboard"], "w") { |clipboard| clipboard.print full_url }
  puts "URL Copied: #{full_url}"
  system("awesome-client", 'Utils.msg("Harambe: Upload Complete")')
else
  puts response_body
end