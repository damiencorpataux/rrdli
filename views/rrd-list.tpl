<style>
  body {
    background: url(http://openclipart.org/people/rejon/rejon_Houses_on_the_Horizon.svg ) center bottom fixed repeat-x;
    background-size: auto 20%;
    background-color: aliceblue !important;
  }
  .list-group {
    opacity: 0.95;
  }
  .list-group-item:hover {
    background-color: #ffe;
  }
  .glyphicon {
    opacity: .25;
  }
  .list-group-item:hover .glyphicon {
    opacity: .75;
  }
</style>
<link href="//netdna.bootstrapcdn.com/bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
<div class="container">
  <div class="page-header">
    <h1>
      Citytool data API
      <small>Prototyping</small>
      <span class="glyphicon glyphicon-leaf pull-right"></span>
    </h1>
  </div>
  <p>
    This web service is a prototype towards fostering the idea of
    <i>a general data interface</i> to access citytool data
    (and other) through the http protocol. Unify data sources and their requests and responses formats.
    In other words, it is a <abbr class="initialism" title="Be sure to read 'How I explained rest to my wife' by Ryan Tomayko, along with his thesis">REST</abbr> data gateway prototype.
  </p>
  <!-- Available urls list -->
  <p>
    <b>Available <span class="initialism">RRD</span>s:</b> ({{len(rrds)}})
  </p>
  <div class="list-group">
  % for rrd in rrds:
    <div class="list-group-item">
      <b>{{rrd['filename']}}</b>
      <ul>
      <!-- rrd summary -->
      <!-- urls list -->
      % for command, url in [(k, rrd[k]) for k in ['info', 'fetch', 'graph', 'igraph']]:
        <li>
          {{command}}: <a href="{{url}}">{{url}}</a>
        </li>
      % end
      </ul>
    </div>
  % end
  </div>
</div>
