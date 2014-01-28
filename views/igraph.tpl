<img class="rrdli-graph" src="{{url}}">
<!-- FIXME: dev purpose: test both smokeping and rrdli connectors-->
<img class="smoke-graph" src="http://wiki-business.lsne.ch/smokeping/smokeping.cgi?displaymode=a;start=1390311760;end=1390912815;target=Local.LocalMachine;hierarchy=">

<script type="text/javascript" src="//code.jquery.com/jquery-2.0.3.min.js"></script>
<script type="text/javascript" src="//code.jquery.com/ui/1.10.3/jquery-ui.min.js"></script>
<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/jquery-mousewheel/3.1.6/jquery.mousewheel.js"></script>
<!-- FIXME: github psuedo-cdn -->
<script_ type="text/javascript" src="http://damiencorpataux.github.io/jquery-smokeping-zoom/zoom.js"></script>
<script type="text/javascript" src="{{get_url('static', file='lib/jquery-zoomly/zoom.js')}}"></script>

<script type="text/javascript">
    $( document ).ready(function() {
        $('.smoke-graph').zoomy({});
        $('.rrdli-graph').zoomy({connector:'rrdli'});
    });
</script>
